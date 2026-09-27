import json
import os
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.core.config import settings
from app.ai_engine.prompts import WEBVERSE_SYSTEM_PROMPT
from app.schemas.ai import CitationSource, ActionProposal

class LLMClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name=settings.LLM_MODEL,
                    system_instruction=WEBVERSE_SYSTEM_PROMPT
                )
            except Exception:
                self.model = None
        else:
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
            for s in retrieved_context["academics"].get("subjects", []):
                citations.append(CitationSource(
                    module="ACADEMICS",
                    title=f"Subject: {s['name']}",
                    detail=f"Attendance: {s['attendance_percentage']} ({s['status']})"
                ))
        if "finance" in retrieved_context:
            f_ctx = retrieved_context["finance"]
            citations.append(CitationSource(
                module="FINANCE",
                title=f"Monthly Budget: {f_ctx.get('current_month')}",
                detail=f"Spent: {f_ctx.get('total_expenses_this_month')} / Remaining: {f_ctx.get('remaining_budget')}"
            ))
        if "life_admin" in retrieved_context:
            for r in retrieved_context["life_admin"].get("pending_reminders", [])[:2]:
                citations.append(CitationSource(
                    module="LIFE_ADMIN",
                    title=f"Reminder: {r['title']}",
                    detail=f"Due at: {r['due_at']}"
                ))

        # If Gemini model is available
        if self.model:
            try:
                chat = self.model.start_chat(history=[])
                for msg in conversation_history[-4:]:
                    # Map history
                    pass
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
            except Exception as e:
                pass # fallback to deterministic synthesizer below

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

        # Check for action trigger (e.g. Add ₹250 for lunch)
        exp_match = re.search(r'(?:add|spent|spend|log)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:for|on)\s*([a-zA-Z0-9\s]+)', q)
        if exp_match:
            amt = float(exp_match.group(1))
            title = exp_match.group(2).strip()
            action_prop = ActionProposal(
                action_type="CREATE_EXPENSE",
                module="FINANCE",
                params={"amount": amt, "title": title, "category_name": "Food" if "lunch" in title or "dinner" in title or "coffee" in title else "General"},
                summary_text=f"Record ₹{amt:,.2f} expense for '{title}'"
            )
            return {
                "text": f"I've prepared an action to record this expense of **₹{amt:,.2f}** for **{title}**. Please confirm below to record it into your Finance ledger.",
                "action_proposal": action_prop
            }

        # Check for attendance query
        if "attendance" in q or "bunk" in q:
            if "academics" in context and context["academics"].get("subjects"):
                subs = context["academics"]["subjects"]
                text_parts.append("### 📚 Academic Attendance Status\n")
                for s in subs:
                    if s["status"] == "SAFE":
                        icon = "🟢"
                    elif s["status"] == "ON_TRACK":
                        icon = "🟡"
                    else:
                        icon = "🔴"
                    text_parts.append(f"- {icon} **{s['name']}**: **{s['attendance_percentage']}** ({s['attended']}/{s['total_classes']} classes). Safe bunks remaining: **{s['bunkable_classes_safe']}**.")
            else:
                text_parts.append("You currently have no recorded subjects. You can add subjects in the Academics tab.")

        # Check for finance spending query
        if "spend" in q or "spent" in q or "food" in q or "budget" in q or "afford" in q:
            if "finance" in context:
                f = context["finance"]
                text_parts.append(f"\n### 💳 Financial Health Overview\n")
                text_parts.append(f"- **Monthly Budget Target:** {f.get('monthly_budget_target')}")
                text_parts.append(f"- **Total Spent This Month:** {f.get('total_expenses_this_month')} ({f.get('budget_used_percentage')} used)")
                text_parts.append(f"- **Remaining Balance:** {f.get('remaining_budget')}")
                text_parts.append(f"- **Daily Burn Rate:** {f.get('average_daily_burn_rate')}")
                
                if f.get("top_spending_categories"):
                    text_parts.append("\n**Top Expense Categories:**")
                    for c in f["top_spending_categories"][:3]:
                        text_parts.append(f"- {c['category']}: **{c['spent']}** ({c['percentage']})")

        # Check for insurance / documents / reminders
        if "insurance" in q or "document" in q or "expire" in q or "reminder" in q:
            if "life_admin" in context:
                l = context["life_admin"]
                text_parts.append(f"\n### 🗂️ Life Admin & Vault Records\n")
                docs = l.get("stored_documents_and_metadata", [])
                if docs:
                    for d in docs:
                        meta = d.get("extracted_fields", {})
                        p_no = meta.get("policy_number", "N/A")
                        exp = meta.get("expiry_date", "N/A")
                        prov = meta.get("provider", "Document")
                        text_parts.append(f"- 📄 **{d['filename']}** ({prov}): Policy No: `{p_no}`, Expiry: **{exp}**")
                
                rems = l.get("pending_reminders", [])
                if rems:
                    text_parts.append("\n**Upcoming Reminders:**")
                    for r in rems[:3]:
                        text_parts.append(f"- ⏰ {r['title']} (Due: {r['due_at']})")

        # Study plan / Cross-module
        if "study plan" in q or "exam" in q:
            if "academics" in context and context["academics"].get("upcoming_exams"):
                exams = context["academics"]["upcoming_exams"]
                text_parts.append(f"\n### 🎯 Personalized Study Strategy\n")
                for e in exams:
                    text_parts.append(f"- Prepare for **{e['subject']} - {e['title']}** scheduled on **{e['exam_date']}**.")

        if not text_parts:
            text_parts.append("I have analyzed your Webverse intelligence matrix across your Academics, Finances, and Life Admin records. How can I assist you further?")

        return {
            "text": "\n".join(text_parts),
            "action_proposal": action_prop
        }

llm_client = LLMClient()
