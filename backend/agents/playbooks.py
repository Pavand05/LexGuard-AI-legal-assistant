"""
Domain Playbooks Architecture for LexGuard-MA
Provides modular, extensible domain-specific playbooks for legal document analysis.
Each playbook uses shared canonical clause IDs and domain-specific expectations.
"""
from typing import Dict, Any, List, Optional
from .clause_taxonomy import CANONICAL_CLAUSE_DEFINITIONS, normalize_to_canonical_id


class DomainPlaybook:
    def __init__(
        self,
        domain_name: str,
        display_name: str,
        supported_types: List[str],
        expected_canonical_ids: List[str],
        applicable_risk_dimensions: List[str],
        jurisdiction_statutes: Dict[str, List[str]],  # Country/Jurisdiction -> list of applicable acts
        applicable_specialist_agents: List[str],
        fact_keys: List[str]
    ):
        self.domain_name = domain_name
        self.display_name = display_name
        self.supported_types = supported_types
        self.expected_canonical_ids = expected_canonical_ids
        self.applicable_risk_dimensions = applicable_risk_dimensions
        self.jurisdiction_statutes = jurisdiction_statutes
        self.applicable_specialist_agents = applicable_specialist_agents
        self.fact_keys = fact_keys

    @property
    def expected_clause_categories(self) -> List[str]:
        """Returns human-readable display names for expected canonical clause IDs."""
        return [
            CANONICAL_CLAUSE_DEFINITIONS.get(cid, {}).get("display", cid)
            for cid in self.expected_canonical_ids
        ]

    @property
    def relevant_research_acts(self) -> List[str]:
        """Backward-compatible access to default/Indian statutory acts."""
        return self.jurisdiction_statutes.get("INDIA", []) or self.jurisdiction_statutes.get("DEFAULT", [])

    def get_statutes_for_jurisdiction(self, country_or_jurisdiction: str) -> List[str]:
        """Retrieve relevant statutory acts for the detected document jurisdiction."""
        clean_j = (country_or_jurisdiction or "").upper().strip()
        
        # Check explicit country/region
        if "INDIA" in clean_j or "BHARAT" in clean_j:
            return self.jurisdiction_statutes.get("INDIA", [])
        elif "US" in clean_j or "USA" in clean_j or "DELAWARE" in clean_j or "CALIFORNIA" in clean_j or "NEW YORK" in clean_j:
            return self.jurisdiction_statutes.get("US", [])
        elif "UK" in clean_j or "ENGLAND" in clean_j or "WALES" in clean_j:
            return self.jurisdiction_statutes.get("UK", [])
        elif "SINGAPORE" in clean_j:
            return self.jurisdiction_statutes.get("SINGAPORE", [])
            
        return self.jurisdiction_statutes.get("DEFAULT", [])


# 1. Real Estate & Property Conveyance Playbook
PROPERTY_PLAYBOOK = DomainPlaybook(
    domain_name="REAL_ESTATE",
    display_name="Real Estate & Immovable Property Conveyancing",
    supported_types=[
        "LAND_SALE_DEED", "LAND_SALE_AGREEMENT", "LAND_LEASE",
        "COMMERCIAL_LEASE", "GIFT_DEED", "MORTGAGE_DEED", "POWER_OF_ATTORNEY"
    ],
    expected_canonical_ids=[
        "PROPERTY_DESCRIPTION", "TITLE_OWNERSHIP", "ENCUMBRANCE_MORTGAGE",
        "CONSIDERATION_PAYMENT", "POSSESSION_REAL_ESTATE", "REGISTRATION_STAMP_DUTY",
        "TAXES_OUTGOINGS", "INDEMNITY_LIABILITY", "DISPUTE_RESOLUTION_ARBITRATION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Compliance", "Operational"],
    jurisdiction_statutes={
        "INDIA": ["Transfer of Property Act, 1882", "Registration Act, 1908", "Indian Stamp Act, 1899", "Specific Relief Act, 1963"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "POSITION_DUTIES", "COMPENSATION_BENEFITS", "EMPLOYMENT_TERM",
        "TERMINATION_NOTICE", "CONFIDENTIALITY_NDA", "NON_COMPETE",
        "NON_SOLICITATION", "IP_ASSIGNMENT", "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Legal", "Compliance", "Operational", "Financial", "IP"],
    jurisdiction_statutes={
        "INDIA": ["Indian Contract Act, 1872", "Industrial Disputes Act, 1947", "Payment of Gratuity Act, 1972"],
        "US": ["Fair Labor Standards Act (FLSA)", "Title VII Civil Rights Act", "State Non-Compete Statutes"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "CONFIDENTIALITY_NDA", "TERMINATION_NOTICE", "GOVERNING_LAW_JURISDICTION",
        "DISPUTE_RESOLUTION_ARBITRATION", "NOTICES_COMMUNICATIONS"
    ],
    applicable_risk_dimensions=["Legal", "Privacy", "IP", "Operational"],
    jurisdiction_statutes={
        "INDIA": ["Indian Contract Act, 1872", "Information Technology Act, 2000"],
        "US": ["Defend Trade Secrets Act (DTSA)", "Uniform Trade Secrets Act (UTSA)"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "LICENSE_GRANT", "IP_ASSIGNMENT", "SLA_SERVICE_LEVEL", "DATA_PROTECTION_PRIVACY",
        "INDEMNITY_LIABILITY", "TERMINATION_NOTICE", "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "IP", "Privacy", "Operational"],
    jurisdiction_statutes={
        "INDIA": ["Copyright Act, 1957", "Information Technology Act, 2000", "Digital Personal Data Protection Act, 2023"],
        "US": ["US Copyright Act 17 USC", "Uniform Computer Information Transactions Act (UCITA)"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "DATA_PROTECTION_PRIVACY", "CONFIDENTIALITY_NDA", "TERMINATION_NOTICE",
        "INDEMNITY_LIABILITY", "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Compliance", "Privacy", "Legal", "Operational"],
    jurisdiction_statutes={
        "INDIA": ["Digital Personal Data Protection Act, 2023", "Information Technology Act, 2000"],
        "US": ["California Consumer Privacy Act (CCPA/CPRA)", "HIPAA", "FTC Act Section 5"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "CONSIDERATION_PAYMENT", "REPRESENTATIONS_WARRANTIES", "INDEMNITY_LIABILITY",
        "TERMINATION_NOTICE", "GOVERNING_LAW_JURISDICTION", "DISPUTE_RESOLUTION_ARBITRATION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Companies Act, 2013", "Indian Partnership Act, 1932", "Foreign Exchange Management Act, 1999"],
        "US": ["Delaware General Corporation Law (DGCL)", "Securities Act of 1933"],
        "DEFAULT": []
    },
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
    expected_canonical_ids=[
        "CONSIDERATION_PAYMENT", "INDEMNITY_LIABILITY", "TERMINATION_NOTICE",
        "REPRESENTATIONS_WARRANTIES", "FORCE_MAJEURE", "DISPUTE_RESOLUTION_ARBITRATION"
    ],
    applicable_risk_dimensions=["Financial", "Operational", "Legal", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Sale of Goods Act, 1930", "Indian Contract Act, 1872", "Arbitration and Conciliation Act, 1996"],
        "US": ["Uniform Commercial Code (UCC) Article 2"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Compliance Agent"
    ],
    fact_keys=[
        "purchase_order_terms", "delivery_deadlines", "payment_days", "late_payment_interest",
        "inspection_window_days", "warranty_months", "liquidated_damages_cap",
        "force_majeure_clause", "termination_notice_days"
    ]
)

# 8. General Open-Set Playbook
GENERAL_PLAYBOOK = DomainPlaybook(
    domain_name="GENERAL_COMMERCIAL",
    display_name="General Legal & Commercial Document",
    supported_types=["OTHER_LEGAL_DOCUMENT", "OTHER", "COMMERCIAL_CONTRACT", "LEGAL_DECLARATION"],
    expected_canonical_ids=[
        "CONSIDERATION_PAYMENT", "TERMINATION_NOTICE", "INDEMNITY_LIABILITY",
        "GOVERNING_LAW_JURISDICTION", "DISPUTE_RESOLUTION_ARBITRATION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Indian Contract Act, 1872", "Arbitration and Conciliation Act, 1996"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Compliance Agent"
    ],
    fact_keys=[
        "term_duration", "payment_amounts", "termination_notice", "liability_cap",
        "governing_law", "jurisdiction_forum", "arbitration_seat"
    ]
)

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
    """
    clean_type = (doc_type or "").upper().strip()
    for pb in PLAYBOOK_REGISTRY:
        if clean_type in [t.upper() for t in pb.supported_types]:
            return pb
            
    if detected_domains:
        for domain in detected_domains:
            norm_dom = domain.upper().strip()
            for pb in PLAYBOOK_REGISTRY:
                if norm_dom in pb.domain_name or any(norm_dom in d for d in pb.domain_name.split("_")):
                    return pb

    return GENERAL_PLAYBOOK
