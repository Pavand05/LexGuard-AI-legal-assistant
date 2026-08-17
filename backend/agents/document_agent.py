"""
Document Intelligence Agent
Responsible for document categorization, entity identification, party mapping,
effective date & jurisdiction resolution, property schedule detection, and structure analysis.
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import extract_entities_and_dates


DOCUMENT_PROFILES = [
    {
        "type": "LAND_SALE_DEED",
        "display": "Deed of Absolute Sale / Land Sale Deed",
        "primary_keywords": ["deed of absolute sale", "sale deed", "deed of sale", "absolute sale", "conveyance deed"],
        "supporting_keywords": ["vendor", "purchaser", "sale consideration", "survey number", "schedule of property", "khata", "sub-registrar", "peaceful possession", "encumbrance", "marketable title", "boundaries"],
        "min_score": 3
    },
    {
        "type": "LAND_SALE_AGREEMENT",
        "display": "Agreement for Sale of Land",
        "primary_keywords": ["agreement for sale", "agreement to sell", "agreement of sale", "memorandum of agreement for sale"],
        "supporting_keywords": ["earnest money", "advance token", "balance consideration", "survey number", "schedule property", "stipulated time", "execute sale deed"],
        "min_score": 3
    },
    {
        "type": "LAND_LEASE",
        "display": "Land Lease / Ground Lease Agreement",
        "primary_keywords": ["lease deed of land", "ground lease", "agricultural lease", "land lease agreement"],
        "supporting_keywords": ["lessor", "lessee", "demised land", "lease rent", "survey number", "term of lease"],
        "min_score": 3
    },
    {
        "type": "COMMERCIAL_LEASE",
        "display": "Commercial Lease / Rent Agreement",
        "primary_keywords": ["commercial lease", "office lease", "tenancy agreement", "rent agreement", "sub-lease"],
        "supporting_keywords": ["lessor", "lessee", "landlord", "tenant", "security deposit", "monthly rent", "lock-in period", "maintenance charges", "fit-out"],
        "min_score": 2
    },
    {
        "type": "GIFT_DEED",
        "display": "Deed of Gift / Settlement Deed",
        "primary_keywords": ["gift deed", "deed of gift", "settlement deed"],
        "supporting_keywords": ["donor", "donee", "natural love and affection", "without monetary consideration", "schedule property"],
        "min_score": 2
    },
    {
        "type": "MORTGAGE_DEED",
        "display": "Mortgage Deed / Deed of Hypothecation",
        "primary_keywords": ["mortgage deed", "deed of mortgage", "simple mortgage", "equitable mortgage"],
        "supporting_keywords": ["mortgagor", "mortgagee", "principal debt", "redemption", "charge on property", "title deeds deposited"],
        "min_score": 2
    },
    {
        "type": "POWER_OF_ATTORNEY",
        "display": "Power of Attorney (GPA / SPA)",
        "primary_keywords": ["power of attorney", "general power of attorney", "special power of attorney", "gpa", "spa"],
        "supporting_keywords": ["principal", "attorney", "constitute and appoint", "lawful attorney", "acts and deeds", "sub-registrar"],
        "min_score": 2
    },
    {
        "type": "NDA",
        "display": "Non-Disclosure Agreement (NDA)",
        "primary_keywords": ["non-disclosure agreement", "nda", "confidentiality agreement", "proprietary information agreement"],
        "supporting_keywords": ["disclosing party", "receiving party", "confidential information", "trade secrets", "non-use", "return of materials"],
        "min_score": 2
    },
    {
        "type": "EMPLOYMENT_AGREEMENT",
        "display": "Employment Agreement / Offer Letter",
        "primary_keywords": ["employment agreement", "offer of employment", "appointment letter", "service agreement with employee"],
        "supporting_keywords": ["employer", "employee", "compensation", "ctc", "salary", "probation", "notice period", "non-solicitation", "duties"],
        "min_score": 2
    },
    {
        "type": "VENDOR_AGREEMENT",
        "display": "Vendor / Supply Agreement",
        "primary_keywords": ["vendor agreement", "supplier agreement", "master supply agreement", "procurement agreement"],
        "supporting_keywords": ["buyer", "supplier", "purchase order", "deliverables", "acceptance criteria", "defects liability", "payment terms"],
        "min_score": 2
    },
    {
        "type": "SERVICE_AGREEMENT",
        "display": "Master Services Agreement (MSA) / SLA",
        "primary_keywords": ["master services agreement", "msa", "service level agreement", "sla", "consultancy agreement", "statement of work", "sow"],
        "supporting_keywords": ["service provider", "client", "deliverables", "milestones", "hourly rate", "service credits", "uptime"],
        "min_score": 2
    },
    {
        "type": "DPA",
        "display": "Data Processing Agreement (DPA)",
        "primary_keywords": ["data processing agreement", "data processing addendum", "dpa", "gdpr addendum", "dpdp compliance agreement"],
        "supporting_keywords": ["data controller", "data processor", "data fiduciary", "data principal", "sub-processor", "technical and organizational measures", "data breach notification"],
        "min_score": 2
    },
    {
        "type": "MOU",
        "display": "Memorandum of Understanding (MOU)",
        "primary_keywords": ["memorandum of understanding", "mou", "letter of intent", "loi", "term sheet"],
        "supporting_keywords": ["non-binding", "preliminary understanding", "collaboration", "definitive agreement", "good faith negotiation"],
        "min_score": 2
    }
]


class DocumentIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Document Intelligence Agent",
            description="Extracts document metadata, classifies document type with multi-factor evidence, maps parties, and resolves jurisdiction.",
            capabilities=["metadata_extraction", "document_classification", "party_mapping", "property_detection", "date_resolution", "jurisdiction_detection"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        filename = context.get("filename", "document.pdf")
        page_texts = context.get("page_texts", [])
        
        extracted = extract_entities_and_dates(text)
        lower_text = text.lower()
        
        # 1. Multi-factor Document Classification
        best_type = "OTHER"
        best_display = "Commercial Contract"
        highest_score = 0
        matched_evidence: List[str] = []

        for profile in DOCUMENT_PROFILES:
            score = 0
            evidence = []
            
            # Primary keyword check (3 points each)
            for kw in profile["primary_keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                    score += 3
                    evidence.append(f"Title/Header keyword: '{kw}'")
                    
            # Supporting keywords check (1 point each)
            for kw in profile["supporting_keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                    score += 1
                    evidence.append(f"Contextual keyword: '{kw}'")
                    
            if score >= profile["min_score"] and score > highest_score:
                highest_score = score
                best_type = profile["type"]
                best_display = profile["display"]
                matched_evidence = evidence[:8]

        # Calibrate confidence
        if highest_score >= 8:
            confidence = 0.98
        elif highest_score >= 5:
            confidence = 0.92
        elif highest_score >= 3:
            confidence = 0.82
        elif highest_score >= 2:
            confidence = 0.65
        else:
            best_type = "OTHER"
            best_display = "Document type uncertain"
            confidence = 0.40
            matched_evidence = ["Insufficient structural or terminology clues to determine definitive document type."]

        # Check for property schedule / survey number clues
        has_property_schedule = bool(re.search(r"(?:schedule\s+of\s+property|schedule\s+[a-z]|survey\s+no|khata\s+no|site\s+no|bounded\s+on)", lower_text))
        if has_property_schedule and "LAND" not in best_type and "LEASE" not in best_type and "MORTGAGE" not in best_type:
            matched_evidence.append("Contains immovable property schedule / survey specifications.")

        summary_msg = f"Document Classified as: {best_display} ({best_type}) [Confidence: {int(confidence*100)}%]. Jurisdiction: {extracted['jurisdiction']}."
        
        metadata = {
            "document_type": best_type,
            "document_type_display": best_display,
            "filename": filename,
            "total_pages": len(page_texts),
            "word_count": len(text.split()),
            "parties": extracted["parties"],
            "dates": extracted["dates"],
            "monetary_values": extracted["monetary_values"],
            "jurisdiction": extracted["jurisdiction"],
            "classification_confidence": confidence,
            "classification_evidence": matched_evidence,
            "has_property_schedule": has_property_schedule
        }

        finding = AgentFindingModel(
            id="doc-struct-01",
            agent="Document Intelligence Agent",
            dimension="Operational",
            category="Document Classification",
            severity="INFORMATIONAL",
            risk_score=10,
            clause_type="Document Classification",
            clause_text=f"Classified: {best_display} ({best_type}) | Parties: {', '.join(extracted['parties'][:2])}",
            page_number=1,
            evidence="; ".join(matched_evidence[:5]),
            claim=f"Document matches {best_display} standard structural profile.",
            reason=f"Multi-factor scoring matched {len(matched_evidence)} key structural indicator(s).",
            recommendation="Verify that contracting entity names, registered addresses, and schedule details align with official records.",
            source_type="DOCUMENT_TEXT",
            verification_status="TEXT_SUPPORTED",
            confidence=confidence
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=confidence,
            summary=summary_msg,
            findings=[finding],
            data=metadata
        )
