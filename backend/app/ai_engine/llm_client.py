import json
import os
import re
from typing import Dict, Any, List, Optional

try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_SDK = "new"
except ImportError:
    try:
        import google.generativeai as genai
        _GENAI_SDK = "legacy"
    except ImportError:
        genai = None
        _GENAI_SDK = "none"

from app.core.config import settings
from app.ai_engine.prompts import WEBVERSE_SYSTEM_PROMPT
from app.schemas.ai import CitationSource, ActionProposal

class LLMClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        self.model_name = settings.LLM_MODEL
        self.model = None  # Legacy fallback

        if self.api_key and _GENAI_SDK == "new":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None
        elif self.api_key and _GENAI_SDK == "legacy":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=WEBVERSE_SYSTEM_PROMPT
                )
            except Exception:
                self.model = None


    async def generate_response(
        self,
        query: str,
        retrieved_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Synthesizes factual answers grounded strictly in retrieved context.
        """
        context_str = json.dumps(retrieved_context, indent=2)
        
        prompt = f"""[RETRIEVED USER FACTS]
{context_str}

[USER INQUIRY]
{query}
"""

        action_proposal = None
        citations: List[CitationSource] = []

        # Populate citations from available contexts
        if "academics" in retrieved_context:
            for s in retrieved_context["academics"].get("subjects", [])[:3]:
                citations.append(CitationSource(
                    module="ACADEMICS",
                    title=f"Subject: {s['name']}",
                    detail=f"Attendance: {s['attendance_percentage']} ({s['status']})"
                ))
            for ex in retrieved_context["academics"].get("upcoming_exams", [])[:2]:
                citations.append(CitationSource(
                    module="ACADEMICS",
                    title=f"Exam: {ex['title']}",
                    detail=f"{ex['subject']} on {ex['exam_date']}"
                ))

        if "finance" in retrieved_context:
            f_ctx = retrieved_context["finance"]
            citations.append(CitationSource(
                module="FINANCE",
                title=f"Monthly Budget: {f_ctx.get('current_month')}",
                detail=f"Spent: {f_ctx.get('total_expenses_this_month')} / Remaining: {f_ctx.get('remaining_budget')}"
            ))

        if "life_admin" in retrieved_context:
            for b in retrieved_context["life_admin"].get("pending_bills", [])[:2]:
                citations.append(CitationSource(
                    module="LIFE_ADMIN",
                    title=f"Bill: {b['title']}",
                    detail=f"Amount: {b['amount']} (Due: {b['due_date']})"
                ))
            for p in retrieved_context["life_admin"].get("active_insurance_policies", [])[:1]:
                citations.append(CitationSource(
                    module="LIFE_ADMIN",
                    title=f"Policy: {p['policy_name']}",
                    detail=f"No: {p['policy_number']} (Exp: {p['expiry_date']})"
                ))
            for r in retrieved_context["life_admin"].get("pending_reminders", [])[:2]:
                citations.append(CitationSource(
                    module="LIFE_ADMIN",
                    title=f"Reminder: {r['title']}",
                    detail=f"Due at: {r['due_at']}"
                ))

        if "cross_module" in retrieved_context:
            cm = retrieved_context["cross_module"]
            overlay = cm.get("intelligence_overlay", {})
            if overlay.get("life_health_score"):
                citations.append(CitationSource(
                    module="CROSS_MODULE",
                    title="Life Health Score",
                    detail=f"{overlay['life_health_score']} · Net liquidity after bills: {overlay.get('net_liquidity_after_bills', 'N/A')}"
                ))
            for alert in overlay.get("critical_alerts", [])[:2]:
                citations.append(CitationSource(
                    module="CROSS_MODULE",
                    title="Critical Alert",
                    detail=alert
                ))

        # If Gemini model is available (new SDK)
        if self.client:
            try:
                full_prompt = WEBVERSE_SYSTEM_PROMPT + "\n\n" + prompt
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt
                )
                raw_text = response.text

                # Parse action proposal block if present
                action_match = re.search(r'```action_proposal\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                clean_text = re.sub(r'```action_proposal\s*(\{.*?\})\s*```', '', raw_text, flags=re.DOTALL).strip()

                if action_match:
                    try:
                        act_data = json.loads(action_match.group(1))
                        action_proposal = ActionProposal(**act_data)
                    except Exception:
                        pass

                return {
                    "content": clean_text,
                    "citations": citations,
                    "action_proposal": action_proposal
                }
            except Exception:
                pass  # fallback to legacy or local synthesizer

        # Legacy google.generativeai fallback
        if self.model:
            try:
                chat = self.model.start_chat(history=[])
                response = chat.send_message(prompt)
                raw_text = response.text

                # Parse action proposal block if present
                action_match = re.search(r'```action_proposal\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                clean_text = re.sub(r'```action_proposal\s*(\{.*?\})\s*```', '', raw_text, flags=re.DOTALL).strip()

                if action_match:
                    try:
                        act_data = json.loads(action_match.group(1))
                        action_proposal = ActionProposal(**act_data)
                    except Exception:
                        pass

                return {
                    "content": clean_text,
                    "citations": citations,
                    "action_proposal": action_proposal
                }
            except Exception:
                pass  # fallback to deterministic synthesizer below

        # Robust Deterministic Context Synthesizer (Instant local response)
        synthesis = self._synthesize_local(query, retrieved_context)
        return {
            "content": synthesis["text"],
            "citations": citations,
            "action_proposal": synthesis.get("action_proposal")
        }

    def _synthesize_local(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        q = query.lower()
        text_parts = []
        action_prop = None

        # 1. Action Triggers: Expense
        exp_match = re.search(r'(?:add|spent|spend|log)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:for|on)\s*([a-zA-Z0-9\s]+)', q)
        if exp_match:
            amt = float(exp_match.group(1))
            title = exp_match.group(2).strip()
            cat = "Food" if any(w in title.lower() for w in ["lunch", "dinner", "coffee", "snack", "burger", "pizza", "meal"]) else "General"
            action_prop = ActionProposal(
                action_type="CREATE_EXPENSE",
                module="FINANCE",
                params={"amount": amt, "title": title, "category_name": cat},
                summary_text=f"Record ₹{amt:,.2f} expense for '{title}'"
            )
            return {
                "text": f"I've prepared an action to record this expense of **₹{amt:,.2f}** for **{title}**.\n\nPlease confirm below to commit this transaction to your Money Manager ledger.",
                "action_proposal": action_prop
            }

        # 2. Action Triggers: Mark Attendance
        att_match = re.search(r'(?:mark|log)\s+([a-zA-Z0-9\s]+?)\s+(?:as\s+)?(present|absent|duty)', q)
        if att_match:
            sub = att_match.group(1).strip()
            stat = att_match.group(2).strip().upper()
            action_prop = ActionProposal(
                action_type="MARK_ATTENDANCE",
                module="ACADEMICS",
                params={"subject_name": sub, "status": stat},
                summary_text=f"Mark {sub} as {stat} for today"
            )
            return {
                "text": f"I've configured an action to log your attendance for **{sub}** as **{stat}**.\n\nClick confirm below to update your StudentOS record.",
                "action_proposal": action_prop
            }

        # 3. Action Triggers: Reminder
        rem_match = re.search(r'(?:remind me to|set reminder for|reminder to)\s+([a-zA-Z0-9\s]+)', q)
        if rem_match:
            title = rem_match.group(1).strip()
            action_prop = ActionProposal(
                action_type="CREATE_REMINDER",
                module="LIFE_ADMIN",
                params={"title": title, "priority": "HIGH" if "urgent" in q else "MEDIUM"},
                summary_text=f"Create reminder: '{title}'"
            )
            return {
                "text": f"I've set up a reminder for: **{title}**.\n\nConfirm below to add it to your Life Admin Vault.",
                "action_proposal": action_prop
            }

        # 4. Action Triggers: Bill
        bill_match = re.search(r'(?:add|create)\s+(?:a\s+)?(?:bill\s+for|bill\s+of)?\s*([a-zA-Z0-9\s]+?)\s*(?:bill)?\s*(?:of|for)?\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:due)?', q)
        if ("bill" in q or "utility" in q) and bill_match:
            title = bill_match.group(1).strip().capitalize()
            amt = float(bill_match.group(2))
            action_prop = ActionProposal(
                action_type="CREATE_BILL",
                module="LIFE_ADMIN",
                params={"title": f"{title} Bill", "amount": amt, "provider": title, "category": "UTILITIES"},
                summary_text=f"Add {title} bill for ₹{amt:,.2f}"
            )
            return {
                "text": f"I've prepared a new bill entry for **{title} Bill** amounting to **₹{amt:,.2f}**.\n\nConfirm below to record it in your Life Admin Vault.",
                "action_proposal": action_prop
            }

        # 5. Cross-Module Synthesis (e.g. Travel affordability with exams & bills)
        is_cross_afford = ("afford" in q or "travel" in q or "trip" in q or "go out" in q) and ("exam" in q or "bill" in q or "budget" in q or "spend" in q)
        if is_cross_afford:
            text_parts.append("### 🌐 Cross-Dimensional Life Synthesis\n")
            
            # Financial evaluation
            f = context.get("finance", {})
            rem_budget = f.get("remaining_budget", "N/A")
            burn_rate = f.get("average_daily_burn_rate", "N/A")
            text_parts.append(f"**Financial Viability:**\n- Remaining Budget: **{rem_budget}**\n- Daily Burn Rate: **{burn_rate}**")
            
            # Bills evaluation
            l = context.get("life_admin", {})
            bills = l.get("pending_bills", [])
            if bills:
                total_bills = sum(b.get("raw_amount", 0) for b in bills)
                text_parts.append(f"- Upcoming Pending Bills: **₹{total_bills:,.2f}** across {len(bills)} bills (e.g., {bills[0]['title']}: {bills[0]['amount']})")
            
            # Academic evaluation
            a = context.get("academics", {})
            exams = a.get("upcoming_exams", [])
            if exams:
                text_parts.append(f"\n**Academic Schedule:**\n- Upcoming Exams: You have **{len(exams)} exam(s)** coming up soon:")
                for ex in exams:
                    text_parts.append(f"  - 📝 **{ex['subject']} ({ex['title']})** on **{ex['exam_date']}**")
            else:
                text_parts.append("\n**Academic Schedule:**\n- No immediate exams scheduled in the next few days.")

            text_parts.append("\n**Omnibar Verdict:**")
            if exams:
                text_parts.append("While your remaining funds might cover short travel expenses, your upcoming exams and pending bills require both study preparation and liquidity. We recommend prioritizing exam preparation or keeping travel budget strictly constrained.")
            else:
                text_parts.append("Your academic schedule is clear of immediate exams. Ensure you allocate enough buffer for your upcoming bills before confirming non-essential travel.")
            
            return {
                "text": "\n".join(text_parts),
                "action_proposal": None
            }

        # 6. Specific Domain: Academics & Attendance
        if "attendance" in q or "bunk" in q or "subject" in q:
            if "academics" in context and context["academics"].get("subjects"):
                subs = context["academics"]["subjects"]
                text_parts.append("### 📚 StudentOS Attendance Standing\n")
                for s in subs:
                    icon = "🟢" if s["status"] == "SAFE" else ("🟡" if s["status"] == "ON_TRACK" else "🔴")
                    text_parts.append(f"- {icon} **{s['name']}** (`{s['code']}`): **{s['attendance_percentage']}** ({s['attended']}/{s['total_classes']} classes). Safe bunks available: **{s['bunkable_classes_safe']}**.")
            else:
                text_parts.append("No active subjects found. You can add subjects in the StudentOS tab.")

        # 7. Specific Domain: Finance
        if "spend" in q or "spent" in q or "budget" in q or "money" in q or "balance" in q:
            if "finance" in context:
                f = context["finance"]
                text_parts.append("### 💳 Money Manager Health\n")
                text_parts.append(f"- **Monthly Budget Target:** {f.get('monthly_budget_target')}")
                text_parts.append(f"- **Total Spent This Month:** {f.get('total_expenses_this_month')} ({f.get('budget_used_percentage')} used)")
                text_parts.append(f"- **Remaining Balance:** {f.get('remaining_budget')}")
                text_parts.append(f"- **Average Burn Rate:** {f.get('average_daily_burn_rate')}")
                
                if f.get("top_spending_categories"):
                    text_parts.append("\n**Top Expense Categories:**")
                    for c in f["top_spending_categories"][:3]:
                        text_parts.append(f"- {c['category']}: **{c['spent']}** ({c['percentage']})")

        # 8. Specific Domain: Life Admin (Bills, Insurance, Documents)
        if "insurance" in q or "policy" in q or "document" in q or "bill" in q or "bills" in q or "reminder" in q or "warranty" in q:
            if "life_admin" in context:
                l = context["life_admin"]
                text_parts.append("### 🗂️ Life Admin Vault Records\n")
                
                bills = l.get("pending_bills", [])
                if bills:
                    text_parts.append("**Pending Bills & Payments:**")
                    for b in bills:
                        text_parts.append(f"- 🧾 **{b['title']}** ({b['provider']}): **{b['amount']}** due on **{b['due_date']}**")

                policies = l.get("active_insurance_policies", [])
                if policies:
                    text_parts.append("\n**Active Insurance & Warranties:**")
                    for p in policies:
                        text_parts.append(f"- 🛡️ **{p['policy_name']}** ({p['provider']}): Policy No: `{p['policy_number']}`, Expires: **{p['expiry_date']}**, Premium: {p['premium']}")

                rems = l.get("pending_reminders", [])
                if rems:
                    text_parts.append("\n**Upcoming Reminders:**")
                    for r in rems[:3]:
                        text_parts.append(f"- ⏰ {r['title']} (Due: {r['due_at']}, Priority: `{r['priority']}`)")

        # 9. Study Plan
        if "study plan" in q or "exam" in q or "syllabus" in q:
            if "academics" in context and context["academics"].get("upcoming_exams"):
                exams = context["academics"]["upcoming_exams"]
                text_parts.append("### 🎯 Personalized Academic Plan\n")
                for e in exams:
                    text_parts.append(f"- Prepare for **{e['subject']} - {e['title']}** on **{e['exam_date']}**.")
                    if e.get("syllabus"):
                        text_parts.append(f"  *Key Syllabus Topics:* {e['syllabus']}")

        if not text_parts:
            text_parts.append("I have analyzed your Webverse intelligence matrix across your Academics, Finances, and Life Admin records. How can I assist you further?")

        return {
            "text": "\n".join(text_parts),
            "action_proposal": action_prop
        }

llm_client = LLMClient()
