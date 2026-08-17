"""
Domain Playbooks Architecture for LexGuard-MA
Provides modular, extensible domain-specific playbooks for legal document analysis.
Adding new legal domains does not require rewriting core orchestrator logic.
"""
from typing import Dict, Any, List, Optional


class DomainPlaybook:
    def __init__(
        self,
        domain_name: str,
        display_name: str,
        supported_types: List[str],
        expected_clause_categories: List[str],
        applicable_risk_dimensions: List[str],
        relevant_research_acts: List[str],
        applicable_specialist_agents: List[str],
        fact_keys: List[str],
        jurisdiction_rules: Dict[str, Any] = None
    ):
        self.domain_name = domain_name
        self.display_name = display_name
        self.supported_types = supported_types
        self.expected_clause_categories = expected_clause_categories
        self.applicable_risk_dimensions = applicable_risk_dimensions
        self.relevant_research_acts = relevant_research_acts
        self.applicable_specialist_agents = applicable_specialist_agents
        self.fact_keys = fact_keys
        self.jurisdiction_rules = jurisdiction_rules or {}


# 1. Real Estate & Property Conveyance Playbook
PROPERTY_PLAYBOOK = DomainPlaybook(
    domain_name="REAL_ESTATE",
    display_name="Real Estate & Immovable Property Conveyancing",
    supported_types=[
        "LAND_SALE_DEED", "LAND_SALE_AGREEMENT", "LAND_LEASE",
        "COMMERCIAL_LEASE", "GIFT_DEED", "MORTGAGE_DEED", "POWER_OF_ATTORNEY"
    ],
    expected_clause_categories=[
        "Property Description & Schedule", "Title & Ownership", "Encumbrance & Mortgage",
        "Consideration & Payment", "Possession", "Registration & Stamp Duty",
        "Taxes & Outgoings", "Indemnity & Liability", "Dispute Resolution & Jurisdiction"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Compliance", "Operational"],
    relevant_research_acts=[
        "Transfer of Property Act, 1882", "Registration Act, 1908",
        "Indian Stamp Act, 1899", "Specific Relief Act, 1963"
    ],
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "property_schedule", "survey_number", "khata_number", "sale_consideration",
        "advance_payment", "balance_payment", "payment_receipt_acknowledged",
        "possession_delivery_date", "possession_already_handed_over", "mortgage_status",
        "encumbrance_status", "court_attachments", "court_jurisdiction", "arbitration_seat",
        "sublease_allowed", "permitted_construction", "renewal_term"
    ]
)

# 2. Employment, Labor & Human Resources Playbook
EMPLOYMENT_PLAYBOOK = DomainPlaybook(
    domain_name="EMPLOYMENT_LABOR",
    display_name="Employment, Labor & Service Contracts",
    supported_types=["EMPLOYMENT_AGREEMENT", "OFFER_LETTER", "INTERNSHIP_AGREEMENT", "CONSULTANCY_AGREEMENT"],
    expected_clause_categories=[
        "Duties & Position", "Compensation & Benefits", "Termination & Notice Period",
        "Confidentiality & Non-Disclosure", "Non-Compete & Restraint", "Non-Solicitation",
        "Intellectual Property Assignment", "Governing Law & Jurisdiction"
    ],
    applicable_risk_dimensions=["Legal", "Compliance", "Operational", "Financial", "IP"],
    relevant_research_acts=[
        "Indian Contract Act, 1872", "Industrial Disputes Act, 1947", "Payment of Gratuity Act, 1972"
    ],
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Privacy & PII Agent"
    ],
    fact_keys=[
        "job_title", "compensation_ctc", "probation_period", "notice_period",
        "termination_for_cause", "termination_without_cause", "non_compete_duration",
        "non_compete_territory", "non_solicitation_duration", "ip_assignment_scope",
        "severance_pay", "dispute_forum"
    ]
)

# 3. Confidentiality & Non-Disclosure Playbook
NDA_PLAYBOOK = DomainPlaybook(
    domain_name="CONFIDENTIALITY_NDA",
    display_name="Non-Disclosure & Trade Secrets",
    supported_types=["NDA", "CONFIDENTIALITY_AGREEMENT", "PROPRIETARY_INFORMATION_AGREEMENT"],
    expected_clause_categories=[
        "Definition of Confidential Information", "Exclusions from Confidentiality",
        "Standard of Care & Non-Use", "Term & Duration", "Return or Destruction of Materials",
        "Governing Law & Jurisdiction", "Remedies & Injunctive Relief"
    ],
    applicable_risk_dimensions=["Legal", "Privacy", "IP", "Operational"],
    relevant_research_acts=[
        "Indian Contract Act, 1872", "Information Technology Act, 2000"
    ],
    applicable_specialist_agents=[
        "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "disclosing_party", "receiving_party", "definition_scope", "marking_requirement",
        "term_years", "survival_period", "return_timeline", "injunctive_relief",
        "jurisdiction_city", "governing_law"
    ]
)

# 4. IP, Software & SaaS Licensing Playbook
IP_TECH_PLAYBOOK = DomainPlaybook(
    domain_name="IP_SOFTWARE_TECH",
    display_name="Intellectual Property, SaaS & Technology Licensing",
    supported_types=[
        "SOFTWARE_LICENSE", "SAAS_AGREEMENT", "SERVICE_AGREEMENT", "EULA",
        "SOURCE_CODE_ESCROW", "MASTER_SERVICES_AGREEMENT"
    ],
    expected_clause_categories=[
        "License Grant & Scope", "Intellectual Property Ownership", "SLA & Uptime Commitments",
        "Data Protection & Security", "Indemnity & IP Infringement", "Limitation of Liability",
        "Termination & Transition Support", "Governing Law & Dispute Resolution"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "IP", "Privacy", "Operational"],
    relevant_research_acts=[
        "Copyright Act, 1957", "Information Technology Act, 2000", "Digital Personal Data Protection Act, 2023"
    ],
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Privacy & PII Agent"
    ],
    fact_keys=[
        "license_type", "user_seats", "ip_ownership", "work_for_hire",
        "uptime_percentage", "service_credits", "liability_cap_amount", "consequential_damages_exclusion",
        "indemnity_infringement", "data_backup_frequency", "transition_period", "forum_selection"
    ]
)

# 5. Data Privacy & Processing Playbook
PRIVACY_PLAYBOOK = DomainPlaybook(
    domain_name="DATA_PRIVACY",
    display_name="Data Privacy & Processing Agreements",
    supported_types=["DATA_PROCESSING_AGREEMENT", "DPA", "PRIVACY_POLICY", "TERMS_OF_SERVICE"],
    expected_clause_categories=[
        "Scope & Purpose of Processing", "Data Principal Rights", "Technical & Organizational Measures",
        "Sub-processor Appointment", "Breach Notification Timeline", "Data Retention & Erasure",
        "Cross-Border Data Transfers", "Audit & Inspection Rights"
    ],
    applicable_risk_dimensions=["Compliance", "Privacy", "Legal", "Operational"],
    relevant_research_acts=[
        "Digital Personal Data Protection Act, 2023", "Information Technology Act, 2000"
    ],
    applicable_specialist_agents=[
        "Compliance Agent", "Privacy & PII Agent", "Obligation Extraction Agent", "Negotiation Agent"
    ],
    fact_keys=[
        "data_fiduciary", "data_processor", "processing_categories", "breach_notice_hours",
        "erasure_timeline", "subprocessor_prior_notice_days", "security_safeguards",
        "audit_frequency", "cross_border_restrictions"
    ]
)

# 6. Corporate, Investment & Shareholders Playbook
CORPORATE_PLAYBOOK = DomainPlaybook(
    domain_name="CORPORATE_GOVERNANCE",
    display_name="Corporate, Shareholding & Joint Ventures",
    supported_types=[
        "SHAREHOLDERS_AGREEMENT", "SHARE_PURCHASE_AGREEMENT", "PARTNERSHIP_AGREEMENT",
        "JOINT_VENTURE_AGREEMENT", "MOU", "LOAN_AGREEMENT"
    ],
    expected_clause_categories=[
        "Capital Structure & Consideration", "Board Representation & Quorum", "Reserved Matters / Veto Rights",
        "Transfer Restrictions (ROFR/ROFO)", "Tag-Along & Drag-Along Rights", "Representations & Warranties",
        "Indemnification & Escrow", "Dispute Resolution & Exit Mechanisms"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    relevant_research_acts=[
        "Companies Act, 2013", "Indian Partnership Act, 1932", "Foreign Exchange Management Act, 1999"
    ],
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "share_count", "share_price", "total_investment", "board_seats", "quorum_rules",
        "reserved_matters_threshold", "rofr_notice_days", "tag_along_threshold",
        "drag_along_threshold", "non_compete_founder", "liquidation_preference", "exit_timeline"
    ]
)

# 7. Commercial Procurement & Supply Playbook
SUPPLY_PLAYBOOK = DomainPlaybook(
    domain_name="COMMERCIAL_SUPPLY",
    display_name="Procurement, Supply & Distribution",
    supported_types=[
        "VENDOR_AGREEMENT", "SUPPLIER_AGREEMENT", "DISTRIBUTOR_AGREEMENT",
        "FRANCHISE_AGREEMENT", "CONSTRUCTION_CONTRACT"
    ],
    expected_clause_categories=[
        "Purchase Orders & Deliverables", "Pricing & Payment Terms", "Quality Standards & Inspection",
        "Defects Liability & Warranty", "Force Majeure", "Termination for Convenience/Cause",
        "Liquidated Damages & Penalties", "Governing Law & Arbitration"
    ],
    applicable_risk_dimensions=["Financial", "Operational", "Legal", "Compliance"],
    relevant_research_acts=[
        "Sale of Goods Act, 1930", "Indian Contract Act, 1872", "Arbitration and Conciliation Act, 1996"
    ],
    applicable_specialist_agents=[
        "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Compliance Agent"
    ],
    fact_keys=[
        "purchase_order_terms", "delivery_deadlines", "payment_days", "late_payment_interest",
        "inspection_window_days", "warranty_months", "liquidated_damages_cap",
        "force_majeure_clause", "termination_notice_days"
    ]
)

# 8. General Open-Set Playbook (Fallback for Unseen / Other Legal Documents)
GENERAL_PLAYBOOK = DomainPlaybook(
    domain_name="GENERAL_COMMERCIAL",
    display_name="General Legal & Commercial Document",
    supported_types=["OTHER_LEGAL_DOCUMENT", "OTHER", "COMMERCIAL_CONTRACT", "LEGAL_DECLARATION"],
    expected_clause_categories=[
        "Parties & Recitals", "Rights & Obligations", "Consideration & Commercial Terms",
        "Term & Termination", "Liability & Indemnity", "Governing Law & Jurisdiction",
        "Dispute Resolution & Notices"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    relevant_research_acts=[
        "Indian Contract Act, 1872", "Arbitration and Conciliation Act, 1996"
    ],
    applicable_specialist_agents=[
        "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Compliance Agent"
    ],
    fact_keys=[
        "term_duration", "payment_amounts", "termination_notice", "liability_cap",
        "governing_law", "jurisdiction_forum", "arbitration_seat"
    ]
)

# Registry of all playbooks
PLAYBOOK_REGISTRY: List[DomainPlaybook] = [
    PROPERTY_PLAYBOOK,
    EMPLOYMENT_PLAYBOOK,
    NDA_PLAYBOOK,
    IP_TECH_PLAYBOOK,
    PRIVACY_PLAYBOOK,
    CORPORATE_PLAYBOOK,
    SUPPLY_PLAYBOOK,
    GENERAL_PLAYBOOK
]


def resolve_domain_playbook(doc_type: str, detected_domains: List[str] = None) -> DomainPlaybook:
    """
    Dynamically select the most suitable DomainPlaybook based on document type and detected domains.
    Never fails; gracefully falls back to GENERAL_PLAYBOOK for unknown document types.
    """
    clean_type = (doc_type or "").upper().strip()
    
    # 1. Exact match on supported document types
    for pb in PLAYBOOK_REGISTRY:
        if clean_type in [t.upper() for t in pb.supported_types]:
            return pb
            
    # 2. Match on detected legal domains
    if detected_domains:
        for domain in detected_domains:
            norm_dom = domain.upper().strip()
            for pb in PLAYBOOK_REGISTRY:
                if norm_dom in pb.domain_name or any(norm_dom in d for d in pb.domain_name.split("_")):
                    return pb

    # 3. Default fallback for open-set / unseen documents
    return GENERAL_PLAYBOOK
