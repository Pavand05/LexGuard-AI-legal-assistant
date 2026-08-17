"""
Legal Document Metadata, Entity, and PII Parsing Tools
"""
import re
from typing import Dict, Any, List


PII_PATTERNS = [
    {
        "type": "Indian PAN Number",
        "pattern": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "mask": "[REDACTED_PAN]"
    },
    {
        "type": "Indian Aadhaar Number",
        "pattern": r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b",
        "mask": "[REDACTED_AADHAAR]"
    },
    {
        "type": "Email Address",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "mask": "[REDACTED_EMAIL]"
    },
    {
        "type": "Phone Number",
        "pattern": r"\b(?:\+91[\-\s]?)?[6789]\d{9}\b",
        "mask": "[REDACTED_PHONE]"
    },
    {
        "type": "Bank Account Number",
        "pattern": r"\b\d{9,18}\b",
        "mask": "[REDACTED_ACCOUNT]"
    }
]


def extract_entities_and_dates(text: str) -> Dict[str, Any]:
    """Extract parties, key dates, jurisdictions, and monetary figures."""
    # Dates extraction (e.g. 15th August 2026, 2024-01-01, 12/05/2025)
    date_pattern = r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b"
    found_dates = list(set(re.findall(date_pattern, text, re.IGNORECASE)))[:5]
    
    # Monetary values extraction (e.g. ₹ 50,000, INR 10,00,000, $5,000, USD 100,000)
    money_pattern = r"(?:₹|Rs\.?|INR|\$|USD|EUR|€)\s*[\d,]+(?:\.\d{2})?(?:\s*(?:lakh|crore|million|billion|k))?"
    found_money = list(set(re.findall(money_pattern, text, re.IGNORECASE)))[:6]
    
    # Governing jurisdiction detection
    jurisdiction = "India"
    jurisdiction_match = re.search(r"(?:courts?\s+of|jurisdiction\s+of|governed\s+by\s+the\s+laws\s+of)\s+([A-Za-z\s,]+?)(?:\.|\n|;|$)", text, re.IGNORECASE)
    if jurisdiction_match:
        jurisdiction = jurisdiction_match.group(1).strip()
        if len(jurisdiction) > 40:
            jurisdiction = jurisdiction[:40]

    # Parties detection
    parties = []
    party_matches = re.findall(r"(?:between|among|by and between)\s+([A-Z][A-Za-z0-9\s,.\-&]+?)\s+(?:and|AND)\s+([A-Z][A-Za-z0-9\s,.\-&]+?)(?:\s*\(|\.|\n)", text)
    if party_matches:
        for p1, p2 in party_matches[:2]:
            p1_clean = re.sub(r"\s+", " ", p1).strip()
            p2_clean = re.sub(r"\s+", " ", p2).strip()
            if len(p1_clean) < 60: parties.append(p1_clean)
            if len(p2_clean) < 60: parties.append(p2_clean)

    return {
        "dates": found_dates,
        "monetary_values": found_money,
        "jurisdiction": jurisdiction,
        "parties": list(set(parties)) if parties else ["Party A (First Party)", "Party B (Second Party)"]
    }


def detect_and_redact_pii(text: str, apply_redaction: bool = False) -> Dict[str, Any]:
    """Scan document for sensitive PII items, return detections and optionally redacted text."""
    detections = []
    redacted_text = text
    
    for item in PII_PATTERNS:
        matches = list(set(re.findall(item["pattern"], text)))
        if matches:
            detections.append({
                "type": item["type"],
                "count": len(matches),
                "samples": [m[:4] + "****" for m in matches[:3]]
            })
            if apply_redaction:
                redacted_text = re.sub(item["pattern"], item["mask"], redacted_text)

    return {
        "has_pii": len(detections) > 0,
        "detections": detections,
        "total_sensitive_items": sum(d["count"] for d in detections),
        "redacted_text": redacted_text if apply_redaction else text
    }
