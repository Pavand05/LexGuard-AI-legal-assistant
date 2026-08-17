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
        "pattern": r"\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b",
        "mask": "[REDACTED_AADHAAR]"
    },
    {
        "type": "Social Security Number (SSN)",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "mask": "[REDACTED_SSN]"
    },
    {
        "type": "Email Address",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "mask": "[REDACTED_EMAIL]"
    },
    {
        "type": "Phone Number",
        "pattern": r"\b(?:\+1[\-\s]?)?\(?[2-9]\d{2}\)?[\-\s]?\d{3}[\-\s]?\d{4}\b|\b(?:\+91[\-\s]?)?[6789]\d{9}\b",
        "mask": "[REDACTED_PHONE]"
    },
    {
        "type": "Bank Account Number",
        "pattern": r"(?i)\b(?:a/c\s*(?:no\.?|num(?:ber)?)?|account\s*(?:no\.?|num(?:ber)?)?|acct\s*(?:no\.?|num(?:ber)?)?|iban)\s*[:#-]?\s*([0-9]{9,18})\b",
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
        jurisdiction = jurisdiction_match.group(1).strip()[:40]

    # Parties extraction
    parties = []
    party_pattern = r"(?:BETWEEN|BY AND BETWEEN|MADE BY|ENTERED INTO BY AND BETWEEN)\s+([A-Z0-9\s,\.\(\)]+?)(?:AND|\&)\s+([A-Z0-9\s,\.\(\)]+?)(?:\.|\n|WHEREAS|NOW)"
    party_match = re.search(party_pattern, text, re.IGNORECASE)
    if party_match:
        p1 = party_match.group(1).split(",")[0].strip()
        p2 = party_match.group(2).split(",")[0].strip()
        if p1 and p2:
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
    """Scan document for sensitive PII items, return detections with exact spans and optionally redacted text."""
    detections = []
    redacted_text = text
    
    for item in PII_PATTERNS:
        raw_matches = list(re.finditer(item["pattern"], text))
        if raw_matches:
            matched_strings = []
            for m in raw_matches:
                # Capture group 1 if present (e.g. for bank account group), else full match
                val = m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)
                matched_strings.append(val.strip())
                
            matched_strings = list(set(matched_strings))
            if matched_strings:
                detections.append({
                    "type": item["type"],
                    "count": len(matched_strings),
                    "samples": [m[:4] + "****" for m in matched_strings[:3]],
                    "matched_values": matched_strings[:3]
                })
                if apply_redaction:
                    redacted_text = re.sub(item["pattern"], item["mask"], redacted_text)

    return {
        "has_pii": len(detections) > 0,
        "detections": detections,
        "total_sensitive_items": sum(d["count"] for d in detections),
        "redacted_text": redacted_text if apply_redaction else text
    }
