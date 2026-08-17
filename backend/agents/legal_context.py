"""
DocumentLegalContext Architecture (LexGuard-MA)
Provides a single canonical legal context model for:
- Governing Law
- Incorporation Jurisdiction
- Court Jurisdiction & Arbitral Seat
- Country and State/Province Resolution
Ensures all agents (Compliance, Research, Citation, Negotiation, Privacy) share the same grounded legal framework.
"""
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DocumentLegalContext:
    country: str                          # "INDIA", "US", "UK", "EU", "SINGAPORE", "UNKNOWN"
    state_or_region: Optional[str]        # e.g. "California", "Delaware", "Karnataka"
    incorporation_jurisdiction: Optional[str] # e.g. "Delaware, USA" (Corporation formation)
    governing_law: str                    # e.g. "Laws of the State of Delaware", "Laws of India"
    court_jurisdiction: Optional[str]     # e.g. "Court of Chancery of the State of Delaware", "Bengaluru Courts"
    arbitration_seat: Optional[str]       # e.g. "San Francisco, California", "Bengaluru"
    jurisdiction_confidence: float        # 0.0 to 1.0
    governing_law_source: str             # "Explicit Governing Law Clause", "Document Scan", "Inferred Default"
    jurisdiction_source: str              # "Explicit Court Jurisdiction Clause", "Document Scan"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)

    def is_us_jurisdiction(self) -> bool:
        return self.country == "US" or (self.state_or_region in [
            "California", "Delaware", "New York", "Texas", "Washington", "Massachusetts", "Illinois", "Florida"
        ])

    def is_indian_jurisdiction(self) -> bool:
        return self.country == "INDIA" or "india" in self.governing_law.lower()


def resolve_document_legal_context(text: str) -> DocumentLegalContext:
    """
    Extracts and separates:
    1. Incorporation Jurisdiction (e.g. Delaware corporation)
    2. Governing Law (e.g. Laws of California / Delaware)
    3. Court Jurisdiction (e.g. Court of Chancery of the State of Delaware)
    4. Arbitration Seat (e.g. LCIA, London)
    """
    lower = text.lower()
    
    # 1. Incorporation Jurisdiction Extraction
    incorp_match = re.search(
        r"(?:a\s+([A-Za-z\s]+?)\s+corporation|incorporated\s+(?:in|under\s+the\s+laws\s+of)\s+(?:the\s+State\s+of\s+)?([A-Za-z\s,]+?)(?:\.|\n|;|,|\)|and))",
        text,
        re.IGNORECASE
    )
    incorp_jur = None
    if incorp_match:
        incorp_jur = (incorp_match.group(1) or incorp_match.group(2) or "").strip()[:40]
        if incorp_jur and not any(k in incorp_jur.lower() for k in ["party", "company", "private", "limited"]):
            incorp_jur = f"{incorp_jur}, USA" if any(s in incorp_jur.lower() for s in ["delaware", "california", "new york", "massachusetts"]) else incorp_jur
        else:
            incorp_jur = None

    # 2. Explicit Governing Law Extraction (High Priority - handles 'construed and enforced in accordance with')
    gov_law_match = re.search(
        r"(?:governed\s+by\s*(?:,\s*and\s+(?:construed|enforced|interpreted)[\w\s,]*in\s+accordance\s+with\s*,?\s*)?(?:the\s+)?(?:internal\s+)?laws\s+of\s+(?:the\s+State\s+of\s+)?)([A-Za-z\s,]+?)(?:\.|\n|;|,|without|\(|and\b)",
        text,
        re.IGNORECASE
    )
    governing_law = "UNKNOWN"
    gov_source = "Document Scan"
    found_gov = None
    if gov_law_match:
        found_gov = gov_law_match.group(1).strip()
        if found_gov and len(found_gov) < 60:
            governing_law = f"Laws of {found_gov}"
            gov_source = "Explicit Governing Law Clause"

    # 3. Court Jurisdiction Extraction (High Priority)
    court_match = re.search(
        r"(?:exclusive\s+jurisdiction\s+of\s+(?:the\s+)?(?:Court\s+of\s+Chancery|courts?|state\s+and\s+federal\s+courts?)\s+(?:of|in|located\s+in)\s+)([A-Za-z\s,]+?)(?:\.|\n|;|,|\(|and)",
        text,
        re.IGNORECASE
    )
    if not court_match:
        court_match = re.search(
            r"(?:exclusive\s+jurisdiction\s+(?:of|in|to)\s+(?:the\s+)?(?:state\s+and\s+federal\s+)?courts?\s+(?:in|at|of|located\s+in)\s+)([A-Za-z\s,]+?)(?:\.|\n|;|,|and)",
            text,
            re.IGNORECASE
        )
    court_jur = None
    court_source = "Document Scan"
    if court_match:
        court_jur = court_match.group(1).strip()[:50]
        court_source = "Explicit Court Jurisdiction Clause"

    # 4. Arbitration Seat Extraction
    arb_match = re.search(
        r"(?:arbitration\s+(?:shall\s+be\s+held|seated|conducted)\s+(?:at|in)\s+([A-Za-z\s,]+?)(?:\.|\n|;|,))",
        text,
        re.IGNORECASE
    )
    arb_seat = None
    if arb_match:
        arb_seat = arb_match.group(1).strip()[:30]

    # 5. Determine Canonical Country and State
    # Prioritize Explicit Governing Law and Court Jurisdiction above party address mentions
    explicit_gov = governing_law.lower()
    explicit_court = (court_jur or "").lower()
    
    country = "UNKNOWN"
    state_or_region = None
    
    if "california" in explicit_gov or "california" in explicit_court:
        country = "US"
        state_or_region = "California"
        if "california" not in governing_law.lower() and gov_source != "Explicit Governing Law Clause":
            governing_law = "Laws of California, USA"
    elif "delaware" in explicit_gov or "delaware" in explicit_court:
        country = "US"
        state_or_region = "Delaware"
        if "delaware" not in governing_law.lower() and gov_source != "Explicit Governing Law Clause":
            governing_law = "Laws of Delaware, USA"
    elif "new york" in explicit_gov or "new york" in explicit_court:
        country = "US"
        state_or_region = "New York"
    elif any(k in explicit_gov or k in explicit_court for k in ["india", "bengaluru", "bangalore", "mumbai", "delhi", "karnataka", "tamil nadu", "maharashtra"]):
        country = "INDIA"
        state_or_region = "India"
        if governing_law == "UNKNOWN":
            governing_law = "Laws of India"
    elif any(k in explicit_gov or k in explicit_court for k in ["england", "wales", "united kingdom", "london"]):
        country = "UK"
        state_or_region = "England & Wales"
        if governing_law == "UNKNOWN":
            governing_law = "Laws of England and Wales"
    elif "singapore" in explicit_gov or "singapore" in explicit_court:
        country = "SINGAPORE"
        state_or_region = "Singapore"
        if governing_law == "UNKNOWN":
            governing_law = "Laws of Singapore"
    else:
        # Fallback to whole text scan if explicit clause was absent
        if "california" in lower and ("california" in lower or "san jose" in lower or "san francisco" in lower or "santa clara" in lower):
            country = "US"
            state_or_region = "California"
            governing_law = "Laws of California, USA"
        elif "delaware" in lower and ("corporation" in lower or "laws of" in lower):
            country = "US"
            state_or_region = "Delaware"
            governing_law = "Laws of Delaware, USA"
        elif any(k in lower for k in ["india", "bengaluru", "karnataka", "sub-registrar", "stamp duty"]):
            country = "INDIA"
            governing_law = "Laws of India"

    confidence = 0.95 if gov_source == "Explicit Governing Law Clause" else 0.80

    return DocumentLegalContext(
        country=country,
        state_or_region=state_or_region,
        incorporation_jurisdiction=incorp_jur,
        governing_law=governing_law,
        court_jurisdiction=court_jur,
        arbitration_seat=arb_seat,
        jurisdiction_confidence=confidence,
        governing_law_source=gov_source,
        jurisdiction_source=court_source
    )
