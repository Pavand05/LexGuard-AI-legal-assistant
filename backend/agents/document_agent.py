"""
Document Intelligence Agent
Responsible for document categorization, entity identification, party mapping,
effective date & jurisdiction resolution, and structure detection.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import extract_entities_and_dates


class DocumentIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Document Intelligence Agent",
            description="Extracts document metadata, identifies contracting parties, effective dates, monetary values, and jurisdiction.",
            capabilities=["metadata_extraction", "party_mapping", "date_resolution", "jurisdiction_detection"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        filename = context.get("filename", "document.pdf")
        page_texts = context.get("page_texts", [])
        
        extracted = extract_entities_and_dates(text)
        
        # Determine document type
        lower = text.lower()
        doc_type = "Commercial Contract"
        if "non-disclosure" in lower or "nda" in lower or "confidentiality agreement" in lower:
            doc_type = "Non-Disclosure Agreement (NDA)"
        elif "employment" in lower or "appointment letter" in lower:
            doc_type = "Employment Agreement"
        elif "lease" in lower or "tenancy" in lower or "rent agreement" in lower:
            doc_type = "Lease & Tenancy Agreement"
        elif "service agreement" in lower or "master services" in lower or "msa" in lower:
            doc_type = "Master Services Agreement (MSA)"
        elif "software license" in lower or "saas" in lower or "eula" in lower:
            doc_type = "Software License / SaaS Agreement"
        elif "data processing" in lower or "dpa" in lower:
            doc_type = "Data Processing Agreement (DPA)"
        elif "internship" in lower:
            doc_type = "Internship Declaration / Agreement"
        elif "declaration" in lower:
            doc_type = "Legal Declaration"

        summary_msg = f"Identified as {doc_type} with {len(page_texts)} page(s). Governing jurisdiction: {extracted['jurisdiction']}."
        
        metadata = {
            "document_type": doc_type,
            "filename": filename,
            "total_pages": len(page_texts),
            "word_count": len(text.split()),
            "parties": extracted["parties"],
            "dates": extracted["dates"],
            "monetary_values": extracted["monetary_values"],
            "jurisdiction": extracted["jurisdiction"]
        }

        finding = AgentFindingModel(
            dimension="Operational",
            risk_level="INFORMATIONAL",
            risk_score=10,
            clause_type="Document Structure",
            clause_text=f"Document Type: {doc_type} | Parties: {', '.join(extracted['parties'][:2])}",
            page_number=1,
            reason=f"Standard structural identification for {doc_type}.",
            recommendation="Ensure all referenced contracting entities and authorized signatories match official registered legal names.",
            citation_status="SUPPORTED",
            confidence=0.94
        )

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=summary_msg,
            findings=[finding],
            data=metadata
        )
