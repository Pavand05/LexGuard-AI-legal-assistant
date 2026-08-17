"""
Domain Playbooks and Canonical Contract Specifications (LexGuard-MA)
Defines expected standard clauses, applicable risk dimensions, and primary statutory
authorities across real estate, employment, NDA, SaaS/tech, privacy, corporate, and open-set commercial contracts.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .clause_taxonomy import CANONICAL_CLAUSE_DEFINITIONS


@dataclass
class DomainPlaybook:
    domain_name: str
    display_name: str
    supported_types: List[str]
    expected_canonical_ids: List[str]
    applicable_risk_dimensions: List[str]
    jurisdiction_statutes: Dict[str, List[str]]
    applicable_specialist_agents: List[str]
    fact_keys: List[str]

    @property
    def expected_clause_categories(self) -> List[str]:
        """Returns human-readable display names for expected canonical clause IDs."""
        return [
            CANONICAL_CLAUSE_DEFINITIONS.get(cid, {}).get("display", cid)
            for cid in self.expected_canonical_ids
        ]

    @property
    def relevant_research_acts(self) -> List[str]:
        """Backward-compatible helper returning default Indian statutes for this domain."""
        return self.jurisdiction_statutes.get("INDIA", self.jurisdiction_statutes.get("DEFAULT", []))

    def get_statutes_for_jurisdiction(self, country: str = "INDIA") -> List[str]:
        """Returns relevant statutory frameworks for a given country code (e.g. INDIA, US, UK)."""
        country_norm = (country or "").upper().strip()
        if country_norm in self.jurisdiction_statutes:
            return self.jurisdiction_statutes[country_norm]
        if "US" in country_norm:
            return self.jurisdiction_statutes.get("US", [])
        return self.jurisdiction_statutes.get("DEFAULT", [])


# ── DOMAIN PLAYBOOK REGISTRY ──────────────────────────────────────────────────

# 1. Real Estate & Conveyancing Playbook
REAL_ESTATE_PLAYBOOK = DomainPlaybook(
    domain_name="REAL_ESTATE",
    display_name="Real Estate & Immovable Property",
    supported_types=[
        "LAND_SALE_DEED", "LAND_SALE_AGREEMENT", "LAND_LEASE", "COMMERCIAL_LEASE",
        "GIFT_DEED", "MORTGAGE_DEED", "POWER_OF_ATTORNEY", "CONVEYANCE_DEED"
    ],
    expected_canonical_ids=[
        "PROPERTY_DESCRIPTION", "TITLE_OWNERSHIP", "CONSIDERATION_PAYMENT",
        "POSSESSION_REAL_ESTATE", "ENCUMBRANCE_MORTGAGE", "INDEMNITY_LIABILITY",
        "REGISTRATION_STAMP_DUTY", "DISPUTE_RESOLUTION_ARBITRATION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Registration Act, 1908", "Transfer of Property Act, 1882", "Indian Stamp Act, 1899", "Indian Contract Act, 1872"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "property_schedule", "survey_no", "consideration_amount", "advance_paid",
        "possession_date", "sub_registrar_office", "prior_deeds", "encumbrance_status"
    ]
)

# 2. Employment & Human Resources Playbook
EMPLOYMENT_PLAYBOOK = DomainPlaybook(
    domain_name="EMPLOYMENT_LABOR",
    display_name="Employment & Executive Contracts",
    supported_types=[
        "EMPLOYMENT_AGREEMENT", "EXECUTIVE_EMPLOYMENT", "OFFER_LETTER",
        "CONSULTANCY_AGREEMENT", "SEVERANCE_AGREEMENT"
    ],
    expected_canonical_ids=[
        "POSITION_DUTIES", "EMPLOYMENT_TERM", "COMPENSATION_BENEFITS",
        "TERMINATION_NOTICE", "CONFIDENTIALITY_NDA", "IP_ASSIGNMENT",
        "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Indian Contract Act, 1872", "Industrial Disputes Act, 1947", "Payment of Gratuity Act, 1972"],
        "US": ["California Business and Professions Code Section 16600", "Fair Labor Standards Act (FLSA)"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Privacy & PII Agent"
    ],
    fact_keys=[
        "job_title", "reporting_manager", "base_salary", "bonus_target", "equity_grant",
        "notice_period_days", "non_compete_duration", "severance_multiplier", "governing_jurisdiction"
    ]
)

# 3. Confidentiality & Non-Disclosure Playbook
NDA_PLAYBOOK = DomainPlaybook(
    domain_name="CONFIDENTIALITY_NDA",
    display_name="Non-Disclosure & Trade Secrets",
    supported_types=["NDA", "CONFIDENTIALITY_AGREEMENT", "PROPRIETARY_INFORMATION_AGREEMENT"],
    expected_canonical_ids=[
        "CONFIDENTIALITY_NDA", "TERMINATION_NOTICE", "GOVERNING_LAW_JURISDICTION",
        "NOTICES_COMMUNICATIONS"
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

# 4. SaaS & Cloud Platform Services Playbook
SAAS_PLAYBOOK = DomainPlaybook(
    domain_name="IP_SOFTWARE_TECH",
    display_name="Software as a Service (SaaS) & Cloud Solutions",
    supported_types=["SAAS_AGREEMENT", "CLOUD_SERVICES_AGREEMENT", "MASTER_SUBSCRIPTION_AGREEMENT"],
    expected_canonical_ids=[
        "SERVICE_SCOPE", "SOFTWARE_LICENSE", "FEES_PAYMENT", "DATA_SECURITY",
        "IP_OWNERSHIP", "INDEMNITY_LIABILITY", "TERMINATION_NOTICE", "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "IP", "Privacy", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Information Technology Act, 2000", "Digital Personal Data Protection Act, 2023", "Copyright Act, 1957"],
        "US": ["Uniform Computer Information Transactions Act (UCITA)", "US Copyright Act 17 USC", "Defend Trade Secrets Act (DTSA)"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent", "Privacy & PII Agent"
    ],
    fact_keys=[
        "service_scope", "subscription_fees", "uptime_sla", "data_security_standards",
        "liability_cap", "indemnity_coverage", "term_years", "governing_law", "court_venue"
    ]
)

# 5. IP, Software & Technology Licensing Playbook
IP_TECH_PLAYBOOK = DomainPlaybook(
    domain_name="IP_SOFTWARE_TECH",
    display_name="Intellectual Property, Software & Technology Licensing",
    supported_types=[
        "SOFTWARE_LICENSE", "SERVICE_AGREEMENT", "EULA",
        "SOURCE_CODE_ESCROW", "MASTER_SERVICES_AGREEMENT"
    ],
    expected_canonical_ids=[
        "SOFTWARE_LICENSE", "IP_OWNERSHIP", "SLA_SERVICE_LEVEL", "DATA_PROTECTION_PRIVACY",
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

# 6. Data Privacy & Processing Playbook
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

# 7. Corporate, Investment & Shareholders Playbook
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

# 8. Commercial Supply & Vendor Procurement Playbook
COMMERCIAL_SUPPLY_PLAYBOOK = DomainPlaybook(
    domain_name="COMMERCIAL_SUPPLY",
    display_name="Commercial Supply & Procurement Contracts",
    supported_types=[
        "VENDOR_AGREEMENT", "SUPPLY_AGREEMENT", "PROCUREMENT_AGREEMENT",
        "DISTRIBUTION_AGREEMENT", "PURCHASE_ORDER"
    ],
    expected_canonical_ids=[
        "CONSIDERATION_PAYMENT", "REPRESENTATIONS_WARRANTIES", "INDEMNITY_LIABILITY",
        "TERMINATION_NOTICE", "FORCE_MAJEURE", "GOVERNING_LAW_JURISDICTION"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Sale of Goods Act, 1930", "Indian Contract Act, 1872", "Micro, Small and Medium Enterprises Development Act, 2006"],
        "US": ["Uniform Commercial Code (UCC) Article 2"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "delivery_schedule", "acceptance_period_days", "warranty_months", "liquidated_damages_cap",
        "payment_due_days", "price_escalation_cap", "minimum_order_quantity"
    ]
)

# 9. Generic / Open-Set Commercial Playbook (Fallback)
GENERIC_COMMERCIAL_PLAYBOOK = DomainPlaybook(
    domain_name="GENERAL_COMMERCIAL",
    display_name="General Commercial Agreement",
    supported_types=["OTHER_LEGAL_DOCUMENT", "COMMERCIAL_CONTRACT", "GENERIC_AGREEMENT"],
    expected_canonical_ids=[
        "TERMINATION_NOTICE", "INDEMNITY_LIABILITY", "GOVERNING_LAW_JURISDICTION",
        "SEVERABILITY", "COMPLETE_AGREEMENT"
    ],
    applicable_risk_dimensions=["Legal", "Financial", "Operational", "Compliance"],
    jurisdiction_statutes={
        "INDIA": ["Indian Contract Act, 1872"],
        "US": ["Restatement (Second) of Contracts"],
        "DEFAULT": []
    },
    applicable_specialist_agents=[
        "Compliance Agent", "Obligation Extraction Agent", "Negotiation Agent", "Redlining Agent"
    ],
    fact_keys=[
        "parties", "effective_date", "term", "consideration", "governing_law"
    ]
)

GENERAL_PLAYBOOK = GENERIC_COMMERCIAL_PLAYBOOK


ALL_PLAYBOOKS: List[DomainPlaybook] = [
    REAL_ESTATE_PLAYBOOK,
    EMPLOYMENT_PLAYBOOK,
    NDA_PLAYBOOK,
    SAAS_PLAYBOOK,
    IP_TECH_PLAYBOOK,
    PRIVACY_PLAYBOOK,
    CORPORATE_PLAYBOOK,
    COMMERCIAL_SUPPLY_PLAYBOOK,
    GENERIC_COMMERCIAL_PLAYBOOK
]


def resolve_domain_playbook(doc_type: str, detected_domains: Optional[List[str]] = None) -> DomainPlaybook:
    """
    Selects the most specific domain playbook based on classified doc_type and detected domains.
    """
    dt_upper = doc_type.upper().strip()
    
    # 1. Match by exact document type
    for pb in ALL_PLAYBOOKS:
        if dt_upper in pb.supported_types:
            return pb
            
    # 2. Match by primary detected domain
    if detected_domains:
        for domain in detected_domains:
            for pb in ALL_PLAYBOOKS:
                if pb.domain_name == domain:
                    return pb
                    
    # 3. Fallback to generic commercial playbook
    return GENERIC_COMMERCIAL_PLAYBOOK
