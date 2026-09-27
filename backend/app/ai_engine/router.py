import re
from typing import List, Dict, Any, Tuple

class AIRouter:
    @staticmethod
    def route_query(query: str) -> Tuple[List[str], str]:
        """
        Determines the relevant modules and intent for a given user prompt.
        Returns: (List[modules], intent)
        """
        q = query.lower()
        modules = []

        # Academic keywords
        academic_keywords = [
            "attendance", "bunk", "subject", "class", "classes", "timetable", "assignment", 
            "assignments", "exam", "exams", "marks", "internal", "daa", "os", "dbms", 
            "study plan", "syllabus", "professor", "college", "lecture", "gpa", "cgpa", 
            "semester", "homework", "test", "quiz"
        ]
        
        # Finance keywords
        finance_keywords = [
            "spend", "spent", "spending", "money", "budget", "cost", "afford", "expense", 
            "expenses", "income", "transaction", "transactions", "food", "travel", 
            "subscription", "subscriptions", "₹", "rupees", "balance", "burn rate", 
            "savings", "salary", "upi", "cash", "account", "pocket money"
        ]

        # Life Admin keywords
        life_keywords = [
            "document", "documents", "pdf", "insurance", "certificate", "policy", "expire", 
            "expiry", "warranty", "reminder", "remind", "appointment", "receipt", "bill", 
            "bills", "utility", "utilities", "rent", "passport", "license", "renewal", 
            "renew", "id card", "aadhaar", "pan card", "due date"
        ]

        # Check hits
        has_academic = any(kw in q for kw in academic_keywords)
        has_finance = any(kw in q for kw in finance_keywords)
        has_life = any(kw in q for kw in life_keywords)

        if has_academic:
            modules.append("ACADEMICS")
        if has_finance:
            modules.append("FINANCE")
        if has_life:
            modules.append("LIFE_ADMIN")

        # Fallback if no specific keyword matched -> Cross-Module / Universal
        if not modules:
            modules = ["ACADEMICS", "FINANCE", "LIFE_ADMIN"]

        # Action intent triggers
        action_verbs = ["add", "mark", "create", "set", "record", "log", "remind me to", "schedule"]
        is_action = any(re.search(rf"\b{re.escape(w)}\b", q) for w in action_verbs)

        if is_action:
            intent = "ACTION"
        elif len(modules) > 1:
            intent = "CROSS_MODULE"
        else:
            intent = "QUERY"

        return modules, intent
