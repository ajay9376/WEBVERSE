import pymupdf as fitz
import re
import json
from typing import Dict, Any, Tuple, List

class DocumentParserService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        text_content = []
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
        except Exception as e:
            text_content.append(f"PDF extraction notice: {str(e)}")
        return "\n".join(text_content).strip()

    @staticmethod
    def extract_metadata_fields(text: str, filename: str) -> Dict[str, Any]:
        """
        Extracts structured fields like policy numbers, dates, providers, amounts, and dates from text.
        """
        metadata: Dict[str, Any] = {}
        text_lower = text.lower()

        # Policy Number extraction
        policy_match = re.search(r'(policy|policy\s*no|policy\s*number|certificate\s*no)[:\s#]+([A-Z0-9\-\/]{5,25})', text, re.IGNORECASE)
        if policy_match:
            metadata["policy_number"] = policy_match.group(2).strip()

        # Expiry / Due Date extraction
        expiry_match = re.search(r'(expiry|expires|valid\s*till|due\s*date|valid\s*upto)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', text, re.IGNORECASE)
        if expiry_match:
            metadata["expiry_date"] = expiry_match.group(2).strip()

        # Premium / Amount extraction
        amount_match = re.search(r'(premium|total\s*amount|amount\s*payable|fee)[:\s₹$Rs\.]*([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
        if amount_match:
            metadata["amount"] = amount_match.group(2).replace(",", "").strip()

        # Provider / Company extraction
        for provider in ["Star Health", "HDFC ERGO", "LIC", "Care Health", "Digit", "SBI Life", "ICICI Lombard", "Coursera", "Udemy", "AWS", "Google Cloud", "Reliance"]:
            if provider.lower() in text_lower:
                metadata["provider"] = provider
                break

        return metadata

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        if not words:
            return []
        
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks
