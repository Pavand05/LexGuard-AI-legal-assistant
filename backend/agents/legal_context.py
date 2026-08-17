"""
DocumentLegalContext Architecture (LexGuard-MA)
Provides a single canonical legal context model for:
- Governing Law
- Incorporation Jurisdiction
- Court Jurisdiction & Arbitral Seat
- Country and State/Province Resolution
Ensures all agents share the identical legal context without downstream agents inventing or defaulting to Indian law.
"""
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentLegalContext(BaseModel):
    country: str = Field(default="UNKNOWN", description="Resolved country e.g. US, INDIA, UK, SINGAPORE")
    state_or_region: Optional[str] = Field(default=None, description="State/Province e.g. California, Delaware, Karnataka")
    incorporation_jurisdiction: Optional[str] = Field(default=None, description="Incorporation state/country of contracting entities")
    governing_law: str = Field(default="UNKNOWN", description="Full explicit governing law text")
    court_jurisdiction: Optional[str] = Field(default=None, description="Explicit civil court jurisdiction forum")
    arbitration_seat: Optional[str] = Field(default=None, description="Explicit arbitral seat")
    jurisdiction_confidence: float = Field(default=0.85, description="Confidence in jurisdiction resolution")
    governing_law_source: str = Field(default="Document Scan", description="Provenance of governing law detection")
    jurisdiction_source: str = Field(default="Document Scan", description="Provenance of court/arbitral forum")

    def is_indian_jurisdiction(self) -> bool:
        """Strict check if document governing law or court jurisdiction is under Indian law."""
        text = f"{self.country} {self.state_or_region} {self.governing_law} {self.court_jurisdiction}".lower()
        if any(us_kw in text for us_kw in ["california", "delaware", "new york", "united states", "u.s.a.", "us law"]):
            return False
        if any(uk_kw in text for uk_kw in ["england and wales", "laws of england", "uk"]):
            return False
        return self.country == "INDIA" or any(k in text for k in ["india", "bharat", "bengaluru", "delhi", "mumbai", "chennai", "kolkata", "hyderabad", "sub-registrar"])

    def is_us_jurisdiction(self) -> bool:
        """Strict check if document governing law is under United States / US State law."""
        text = f"{self.country} {self.state_or_region} {self.governing_law} {self.court_jurisdiction}".lower()
        return self.country == "US" or any(k in text for k in ["california", "delaware", "new york", "united states", "u.s.a.", "laws of the state of"])


def resolve_document_legal_context(text: str) -> DocumentLegalContext:
    """
    Extracts and separates:
    1. Incorporation Jurisdiction (e.g. Delaware corporation)
    2. Governing Law (e.g. Laws of California)
    3. Court Jurisdiction (e.g. Courts of San Francisco, California)
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
            incorp_jur = f"{incorp_jur}, USA" if "delaware" in incorp_jur.lower() or "california" in incorp_jur.lower() else incorp_jur
        else:
            incorp_jur = None

    # 2. Explicit Governing Law Extraction
    gov_law_match = re.search(
        r"(?:governed\s+by\s+(?:and\s+construed\s+in\s+accordance\s+with\s+)?(?:the\s+)?(?:internal\s+)?laws\s+of\s+(?:the\s+State\s+of\s+)?)([A-Za-z\s,]+?)(?:\.|\n|;|,|without|and|\()",
        text,
        re.IGNORECASE
    )
    governing_law = "UNKNOWN"
    gov_source = "Document Scan"
    if gov_law_match:
        found_gov = gov_law_match.group(1).strip()
        if found_gov and len(found_gov) < 60:
            governing_law = f"Laws of {found_gov}"
            gov_source = "Explicit Governing Law Clause"

    # 3. Court Jurisdiction Extraction
    court_match = re.search(
        r"(?:exclusive\s+jurisdiction\s+(?:of|in|to)\s+(?:the\s+)?(?:state\s+and\s+federal\s+)?courts?\s+(?:in|at|of)\s+)([A-Za-z\s,]+?)(?:\.|\n|;|,|and)",
        text,
        re.IGNORECASE
    )
    court_jur = None
    court_source = "Document Scan"
    if court_match:
        court_jur = court_match.group(1).strip()[:40]
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
    combined_gov = f"{governing_law} {court_jur}".lower()
    
    country = "UNKNOWN"
    state_or_region = None
    
    if "california" in combined_gov:
        country = "US"
        state_or_region = "California"
    elif "delaware" in combined_gov:
        country = "US"
        state_or_region = "Delaware"
    elif "new york" in combined_gov:
        country = "US"
        state_or_region = "New York"
    elif any(k in combined_gov for k in ["united states", "u.s.a.", "state of"]):
        country = "US"
        state_or_region = "US General"
    elif any(k in combined_gov for k in ["england and wales", "laws of england", "uk", "london"]):
        country = "UK"
        state_or_region = "England & Wales"
    elif any(k in combined_gov for k in ["singapore", "siac"]):
        country = "SINGAPORE"
        state_or_region = "Singapore"
    elif any(k in combined_gov for k in ["india", "bharat", "bengaluru", "delhi", "mumbai", "chennai", "kolkata", "hyderabad"]):
        country = "INDIA"
        state_or_region = "Karnataka" if "bengaluru" in combined_gov or "karnataka" in combined_gov else "Central India"
    else:
        # Fallback to general scan if explicit clause wasn't captured
        if "california" in lower:
            country = "US"
            state_or_region = "California"
            if governing_law == "UNKNOWN":
                governing_law = "Laws of California, USA"
        elif "delaware" in lower and not "india" in lower:
            country = "US"
            state_or_region = "Delaware"
            if governing_law == "UNKNOWN":
                governing_law = "Laws of Delaware, USA"
        elif any(k in lower for k in ["bengaluru", "delhi", "mumbai", "sub-registrar", "khata", "survey no"]):
            country = "INDIA"
            state_or_region = "India"
            if governing_law == "UNKNOWN":
                governing_law = "Laws of India"

    return DocumentLegalContext(
        country=country,
        state_or_region=state_or_region,
        incorporation_jurisdiction=incorp_jur,
        governing_law=governing_law if governing_law != "UNKNOWN" else (f"Laws of {state_or_region}" if state_or_region else "Unspecified Jurisdiction"),
        court_jurisdiction=court_jur,
        arbitration_seat=arb_seat,
        jurisdiction_confidence=0.95 if gov_law_match else 0.80,
        governing_law_source=gov_source,
        jurisdiction_source=court_source
    )
