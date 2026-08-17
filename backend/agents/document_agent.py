"""
Document Intelligence Agent (LexGuard-MA)
Performs open-set document classification, primary vs referenced agreement resolution,
clean multi-domain detection, party mapping, and canonical DocumentLegalContext resolution.
"""
import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from agent_tools.document_tools import extract_entities_and_dates
from .legal_context import resolve_document_legal_context, DocumentLegalContext


DOCUMENT_TAXONOMY = [
    # --- SaaS, Cloud & Technology Licensing ---
    {
        "type": "SAAS_AGREEMENT",
        "display": "Software-as-a-Service (SaaS) Agreement / Cloud SLA",
        "domain": "IP_SOFTWARE_TECH",
        "primary_keywords": [
            "software as a service agreement", "software as a service", "saas agreement",
            "cloud services agreement", "master subscription agreement", "saas terms of service",
            "hosted services agreement"
        ],
        "supporting_keywords": [
            "subscriber", "cloud service", "uptime", "sla", "service credits", "revenue share",
            "subscription fees", "platform availability", "cloud hosting", "api access", "customer data"
        ],
        "min_score": 2
    },
    {
        "type": "SOFTWARE_LICENSE",
        "display": "Software License Agreement / EULA",
        "domain": "IP_SOFTWARE_TECH",
        "primary_keywords": [
            "software license agreement", "end user license agreement", "eula",
            "software licensing agreement", "proprietary software license"
        ],
        "supporting_keywords": [
            "licensor", "licensee", "licensed software", "grant of license", "intellectual property",
            "derivative works", "source code", "object code"
        ],
        "min_score": 2
    },

    # --- Real Estate & Conveyancing ---
    {
        "type": "LAND_SALE_DEED",
        "display": "Deed of Absolute Sale / Land Sale Deed",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["deed of absolute sale", "sale deed", "deed of sale", "absolute sale", "conveyance deed"],
        "supporting_keywords": ["vendor", "purchaser", "sale consideration", "survey number", "schedule of property", "khata", "sub-registrar", "peaceful possession", "encumbrance", "marketable title", "boundaries"],
        "min_score": 3
    },
    {
        "type": "LAND_SALE_AGREEMENT",
        "display": "Agreement for Sale of Land / Property",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["agreement for sale", "agreement to sell", "agreement of sale", "memorandum of agreement for sale"],
        "supporting_keywords": ["earnest money", "advance token", "balance consideration", "survey number", "schedule property", "stipulated time", "execute sale deed"],
        "min_score": 3
    },
    {
        "type": "LAND_LEASE",
        "display": "Agricultural / Ground Land Lease Agreement",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["lease deed of land", "ground lease", "agricultural lease", "land lease agreement", "agricultural land lease"],
        "supporting_keywords": ["lessor", "lessee", "demised land", "lease rent", "survey number", "term of lease", "cultivation"],
        "min_score": 3
    },
    {
        "type": "COMMERCIAL_LEASE",
        "display": "Commercial Lease / Tenancy Agreement",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["commercial lease", "office lease", "tenancy agreement", "rent agreement", "sub-lease", "lease deed of premises"],
        "supporting_keywords": ["lessor", "lessee", "landlord", "tenant", "security deposit", "monthly rent", "lock-in period", "maintenance charges", "fit-out"],
        "min_score": 2
    },
    {
        "type": "GIFT_DEED",
        "display": "Deed of Gift / Settlement Deed",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["gift deed", "deed of gift", "settlement deed"],
        "supporting_keywords": ["donor", "donee", "natural love and affection", "without monetary consideration", "schedule property"],
        "min_score": 2
    },
    {
        "type": "MORTGAGE_DEED",
        "display": "Mortgage Deed / Deed of Hypothecation",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["mortgage deed", "deed of mortgage", "simple mortgage", "equitable mortgage"],
        "supporting_keywords": ["mortgagor", "mortgagee", "principal debt", "redemption", "charge on property", "title deeds deposited"],
        "min_score": 2
    },
    {
        "type": "POWER_OF_ATTORNEY",
        "display": "Power of Attorney (GPA / SPA)",
        "domain": "REAL_ESTATE",
        "primary_keywords": ["power of attorney", "general power of attorney", "special power of attorney", "gpa", "spa"],
        "supporting_keywords": ["principal", "attorney", "constitute and appoint", "lawful attorney", "acts and deeds", "sub-registrar"],
        "min_score": 2
    },

    # --- Employment & HR ---
    {
        "type": "EMPLOYMENT_AGREEMENT",
        "display": "Employment Agreement / Executive Contract",
        "domain": "EMPLOYMENT_LABOR",
        "primary_keywords": [
            "employment agreement", "employment contract", "executive employment",
            "service agreement with employee", "executive employment agreement",
            "employment and confidentiality agreement"
        ],
        "supporting_keywords": ["employer", "employee", "executive", "compensation", "ctc", "salary", "probation", "notice period", "non-solicitation", "duties", "severance", "inventions assignment", "base salary"],
        "min_score": 2
    },
    {
        "type": "OFFER_LETTER",
        "display": "Employment Offer Letter / Appointment Letter",
        "domain": "EMPLOYMENT_LABOR",
        "primary_keywords": ["offer letter", "offer of employment", "letter of appointment", "appointment letter"],
        "supporting_keywords": ["joining date", "annual ctc", "base salary", "designation", "reporting to", "terms of employment"],
        "min_score": 2
    },

    # --- Confidentiality & Non-Disclosure ---
    {
        "type": "NDA",
        "display": "Non-Disclosure Agreement (NDA) / Secrecy Deed",
        "domain": "CONFIDENTIALITY_NDA",
        "primary_keywords": [
            "non-disclosure agreement", "mutual non-disclosure", "confidentiality agreement",
            "proprietary information agreement", "unilateral nda", "mutual non-disclosure and confidentiality agreement"
        ],
        "supporting_keywords": ["disclosing party", "receiving party", "confidential information", "trade secrets", "non-use", "return of materials", "injunctive relief", "evaluation material", "potential transaction"],
        "min_score": 2
    },

    # --- Privacy & Data Governance ---
    {
        "type": "DATA_PROCESSING_AGREEMENT",
        "display": "Data Processing Agreement (DPA) / DPDP Addendum",
        "domain": "DATA_PRIVACY",
        "primary_keywords": ["data processing agreement", "data processing addendum", "dpa", "gdpr addendum", "dpdp compliance addendum"],
        "supporting_keywords": ["data controller", "data processor", "data fiduciary", "data principal", "sub-processor", "technical measures", "breach notification"],
        "min_score": 2
    },
    {
        "type": "PRIVACY_POLICY",
        "display": "Website / App Privacy Policy",
        "domain": "DATA_PRIVACY",
        "primary_keywords": ["privacy policy", "privacy statement", "data privacy notice", "information security policy"],
        "supporting_keywords": ["personal data", "cookies", "third-party tracking", "data collection", "your rights", "grievance officer"],
        "min_score": 2
    },
    {
        "type": "TERMS_OF_SERVICE",
        "display": "Terms of Service / Terms & Conditions",
        "domain": "DATA_PRIVACY",
        "primary_keywords": ["terms of service", "terms and conditions", "terms of use", "user agreement"],
        "supporting_keywords": ["acceptable use", "account registration", "user conduct", "prohibited activities", "termination of access"],
        "min_score": 2
    },

    # --- Corporate, Investment & Commercial Supply ---
    {
        "type": "SHAREHOLDERS_AGREEMENT",
        "display": "Shareholders' Agreement (SHA) / Stockholders Agreement",
        "domain": "CORPORATE_GOVERNANCE",
        "primary_keywords": ["shareholders agreement", "shareholders' agreement", "sha", "investor rights agreement"],
        "supporting_keywords": ["equity shares", "board representation", "reserved matters", "rofr", "tag along", "drag along", "liquidation preference", "quorum"],
        "min_score": 2
    },
    {
        "type": "SHARE_PURCHASE_AGREEMENT",
        "display": "Share Purchase Agreement (SPA)",
        "domain": "CORPORATE_GOVERNANCE",
        "primary_keywords": ["share purchase agreement", "spa", "stock purchase agreement"],
        "supporting_keywords": ["purchased shares", "purchase price", "closing conditions", "indemnification escrow", "reps and warranties"],
        "min_score": 2
    },
    {
        "type": "PARTNERSHIP_AGREEMENT",
        "display": "Partnership Deed / LLP Agreement",
        "domain": "CORPORATE_GOVERNANCE",
        "primary_keywords": ["partnership deed", "partnership agreement", "llp agreement", "limited liability partnership agreement"],
        "supporting_keywords": ["partners", "capital contribution", "profit sharing ratio", "drawings", "admission of partner", "dissolution"],
        "min_score": 2
    },
    {
        "type": "VENDOR_AGREEMENT",
        "display": "Vendor / Supply Agreement",
        "domain": "COMMERCIAL_SUPPLY",
        "primary_keywords": ["vendor agreement", "supplier agreement", "master supply agreement", "procurement agreement"],
        "supporting_keywords": ["buyer", "supplier", "purchase order", "deliverables", "acceptance criteria", "defects liability", "payment terms"],
        "min_score": 2
    },
    {
        "type": "SERVICE_AGREEMENT",
        "display": "Master Services Agreement (MSA) / Statement of Work",
        "domain": "COMMERCIAL_SUPPLY",
        "primary_keywords": ["master services agreement", "msa", "service agreement", "statement of work", "sow", "consultancy agreement"],
        "supporting_keywords": ["service provider", "client", "deliverables", "milestones", "hourly rate", "acceptance", "ip rights"],
        "min_score": 2
    },
    {
        "type": "LOAN_AGREEMENT",
        "display": "Loan Agreement / Facility Agreement",
        "domain": "CORPORATE_GOVERNANCE",
        "primary_keywords": ["loan agreement", "facility agreement", "credit facility agreement", "promissory note"],
        "supporting_keywords": ["borrower", "lender", "principal amount", "interest rate", "repayment schedule", "default interest", "security"],
        "min_score": 2
    },
    {
        "type": "MOU",
        "display": "Memorandum of Understanding (MOU) / Letter of Intent",
        "domain": "CORPORATE_GOVERNANCE",
        "primary_keywords": ["memorandum of understanding", "mou", "letter of intent", "loi", "term sheet"],
        "supporting_keywords": ["non-binding", "preliminary understanding", "collaboration", "definitive agreement", "good faith negotiation"],
        "min_score": 2
    }
]

# Unambiguous semantic domain keywords to prevent false cross-domain activation
LEGAL_DOMAINS_CRITERIA = {
    "REAL_ESTATE": [
        r"\b(real\s+estate|immovable\s+property|land\s+sale|lease\s+deed|ground\s+lease|mortgage\s+deed|gift\s+deed|conveyance\s+deed|schedule\s+of\s+property|survey\s+no|khata\s+no|demised\s+land|sub-registrar)\b"
    ],
    "EMPLOYMENT_LABOR": [
        r"\b(executive\s+employment|employment\s+agreement|offer\s+of\s+employment|base\s+salary|annual\s+ctc|probation\s+period|terms\s+of\s+employment|employer\s+and\s+employee|employee\s+benefit\s+plan|severance\s+benefit|inventions\s+assignment)\b"
    ],
    "CONFIDENTIALITY_NDA": [
        r"\b(confidential\s+information|non[- ]?disclosure|trade\s+secrets?|receiving\s+party|disclosing\s+party|proprietary\s+information)\b"
    ],
    "IP_SOFTWARE_TECH": [
        r"\b(software\s+as\s+a\s+service|saas|cloud\s+services?|software\s+license|source\s+code|sla\s+uptime|uptime\s+percentage|service\s+credits|revenue\s+share|subscriber\s+data|hosted\s+services?)\b"
    ],
    "DATA_PRIVACY": [
        r"\b(personal\s+data|data\s+processing\s+agreement|data\s+fiduciary|data\s+processor|gdpr|dpdp\s+act|privacy\s+policy|breach\s+notification)\b"
    ],
    "CORPORATE_GOVERNANCE": [
        r"\b(shareholders\s+agreement|board\s+of\s+directors|equity\s+shares|series\s+[a-z]\s+preferred|partnership\s+deed|investor\s+rights|rofr)\b"
    ],
    "COMMERCIAL_SUPPLY": [
        r"\b(purchase\s+orders?|supplier\s+agreement|procurement\s+agreement|master\s+supply|defects\s+liability\s+period|vendor\s+agreement)\b"
    ]
}


class DocumentIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Document Intelligence Agent",
            description="Performs open-set document classification, primary vs referenced agreement extraction, multi-domain detection, and DocumentLegalContext resolution.",
            capabilities=["metadata_extraction", "open_set_classification", "referenced_documents_extraction", "domain_detection", "party_mapping", "legal_context_resolution"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        filename = context.get("filename", "document.pdf")
        page_texts = context.get("page_texts", [])
        
        extracted = extract_entities_and_dates(text)
        lower_text = text.lower()
        header_text = lower_text[:1200]  # First ~1200 chars containing title, recital & preamble
        
        # 1. Canonical Legal Context Resolution (Governing Law vs Incorporation vs Jurisdiction)
        legal_context: DocumentLegalContext = resolve_document_legal_context(text)

        # 2. Extract Referenced / Incorporated Agreements
        referenced_documents: List[Dict[str, Any]] = []
        ref_patterns = [
            (r"(?:entered\s+into|parties\s+have\s+entered\s+into|subject\s+to\s+the\s+terms\s+of|incorporated\s+by\s+reference|prior\s+to\s+this\s+Agreement,\s+the\s+Parties\s+executed)\s+(?:a|that\s+certain)?\s*([A-Za-z0-9\s,\-]{4,60}?(?:Non-Disclosure\s+Agreement|Confidentiality\s+Agreement|Master\s+Agreement|NDA|DPA|SLA))\b", "INCORPORATED"),
            (r"(?:pursuant\s+to|governed\s+by\s+the\s+terms\s+of)\s+(?:a|that\s+certain)?\s*([A-Za-z0-9\s,\-]{4,60}?(?:Non-Disclosure\s+Agreement|Confidentiality\s+Agreement|Statement\s+of\s+Work|Schedule\s+[A-Z\d]+))\b", "REFERENCED")
        ]
        seen_refs = set()
        for pat, status in ref_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                ref_name = m.group(1).strip()
                ref_type = "NDA" if any(k in ref_name.lower() for k in ["non-disclosure", "confidentiality", "nda"]) else "OTHER_AGREEMENT"
                if ref_name.lower() not in seen_refs:
                    seen_refs.add(ref_name.lower())
                    referenced_documents.append({
                        "name": ref_name,
                        "type": ref_type,
                        "status": status,
                        "evidence": m.group(0)[:140]
                    })

        # 3. Strict Semantic Domain Detection
        detected_domains: List[str] = []
        for domain_name, pattern_list in LEGAL_DOMAINS_CRITERIA.items():
            hits = 0
            for pat in pattern_list:
                matches = list(re.finditer(pat, lower_text, re.IGNORECASE))
                hits += len(matches)
            if hits >= 2:
                if domain_name not in detected_domains:
                    detected_domains.append(domain_name)
                    
        if not detected_domains:
            detected_domains = ["GENERAL_COMMERCIAL"]

        # 4. Open-Set Document Taxonomy Classification with Title & Header Hierarchy
        best_type = "OTHER_LEGAL_DOCUMENT"
        best_display = "Other Legal / Commercial Document"
        best_domain = detected_domains[0]
        highest_score = 0
        matched_evidence: List[str] = []
        secondary_types: List[str] = []

        for profile in DOCUMENT_TAXONOMY:
            score = 0
            evidence = []
            
            # Level 1: Explicit Document Title / Header Match (First 1200 characters) - Highest Priority
            for kw in profile["primary_keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", header_text):
                    score += 25  # Massive weight for title/preamble match
                    evidence.append(f"Title / Header match: '{kw}'")
                elif re.search(rf"\b{re.escape(kw)}\b", lower_text):
                    score += 4
                    evidence.append(f"Body keyword match: '{kw}'")
                    
            for kw in profile["supporting_keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                    score += 1
                    evidence.append(f"Contextual: '{kw}'")
                    
            # Demote NDA score if NDA is only a referenced agreement inside a non-NDA title
            if profile["type"] == "NDA" and referenced_documents:
                # If title had SaaS, Software License, Master Agreement, or Employment, demote NDA body score
                if any(k in header_text for k in ["software as a service", "saas", "software license", "employment agreement", "commercial lease"]):
                    score = min(score, 3)

            if score >= profile["min_score"]:
                if score > highest_score:
                    if highest_score >= 4 and best_type != "OTHER_LEGAL_DOCUMENT" and best_type not in secondary_types:
                        secondary_types.append(best_type)
                    highest_score = score
                    best_type = profile["type"]
                    best_display = profile["display"]
                    best_domain = profile["domain"]
                    matched_evidence = evidence[:8]
                elif score >= 4 and profile["type"] != best_type and profile["type"] not in secondary_types:
                    secondary_types.append(profile["type"])

        # Calibrate Confidence
        if highest_score >= 20:
            confidence = 0.98
        elif highest_score >= 8:
            confidence = 0.94
        elif highest_score >= 5:
            confidence = 0.88
        elif highest_score >= 3:
            confidence = 0.78
        elif highest_score >= 2:
            confidence = 0.65
        else:
            best_type = "OTHER_LEGAL_DOCUMENT"
            best_display = "Other Legal / Commercial Document"
            confidence = 0.50
            matched_evidence = [f"Unseen / open-set structure. Matched legal domains: {', '.join(detected_domains)}."]

        # Ensure primary classified domain is in detected_domains
        if best_domain not in detected_domains and best_type != "OTHER_LEGAL_DOCUMENT":
            detected_domains.insert(0, best_domain)

        # De-duplicate domain list preserving order
        unique_domains: List[str] = []
        for d in detected_domains:
            if d not in unique_domains:
                unique_domains.append(d)

        has_property_schedule = bool(re.search(r"(?:schedule\s+of\s+property|schedule\s+[a-z]|survey\s+no|khata\s+no|site\s+no|bounded\s+on)", lower_text))

        summary_msg = f"Document Classified: {best_display} ({best_type}) [Confidence: {int(confidence*100)}%]. Domains: {', '.join(unique_domains)}. Governing Law: {legal_context.governing_law} ({legal_context.country})."
        
        metadata = {
            "document_type": best_type,
            "primary_type": best_type,
            "secondary_types": secondary_types,
            "document_type_display": best_display,
            "detected_domains": unique_domains,
            "primary_domain": best_domain,
            "secondary_domains": unique_domains[1:] if len(unique_domains) > 1 else [],
            "referenced_documents": referenced_documents,
            "filename": filename,
            "total_pages": len(page_texts),
            "word_count": len(text.split()),
            "parties": extracted["parties"],
            "dates": extracted["dates"],
            "monetary_values": extracted["monetary_values"],
            "legal_context": legal_context.to_dict(),
            "applicable_law": legal_context.governing_law,
            "court_jurisdiction": legal_context.court_jurisdiction or "Competent Courts",
            "arbitration_seat": legal_context.arbitration_seat,
            "country": legal_context.country,
            "state_or_region": legal_context.state_or_region,
            "incorporation_jurisdiction": legal_context.incorporation_jurisdiction,
            "classification_confidence": confidence,
            "classification_evidence": matched_evidence,
            "has_property_schedule": has_property_schedule,
            "is_open_set": best_type == "OTHER_LEGAL_DOCUMENT"
        }

        finding = AgentFindingModel(
            id="doc-struct-01",
            agent="Document Intelligence Agent",
            dimension="Operational",
            category="Document Classification",
            severity="INFORMATIONAL",
            risk_score=10,
            clause_type="Document Classification",
            clause_text=f"Classified: {best_display} ({best_type}) | Governing Law: {legal_context.governing_law} | Domains: {', '.join(unique_domains)}",
            page_number=1,
            evidence="; ".join(matched_evidence[:5]),
            claim=f"Document identified as {best_display} under {best_domain} legal domain.",
            reason=f"Open-set taxonomy analysis matched {len(matched_evidence)} indicator(s). Governing law: {legal_context.governing_law}.",
            recommendation="Review contracting entity capacity and ensure all schedules match official records.",
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
