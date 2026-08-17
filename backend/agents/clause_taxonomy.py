"""
Canonical Clause Taxonomy & Domain Compatibility Matrix (LexGuard-MA)
Defines shared canonical clause identifiers, category aliases, descriptions,
and domain compatibility affinities across legal domains.
"""
from typing import Dict, Any, List, Set, Optional


# ── 1. CANONICAL CLAUSE DEFINITIONS ──────────────────────────────────────────
CANONICAL_CLAUSE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # --- Employment & HR ---
    "EMPLOYMENT_TERM": {
        "display": "Employment Term & Tenure",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "employment term", "period of employment", "employment period",
            "term of employment", "appointment duration", "tenure",
            "duration of employment", "employment duration"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "POSITION_DUTIES": {
        "display": "Position, Duties & Scope",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "position, duties & scope", "position and duties", "position & duties",
            "duties & position", "job title", "responsibilities", "duties",
            "reporting structure", "scope of employment", "title & responsibilities",
            "executive duties"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "COMPENSATION_BENEFITS": {
        "display": "Compensation, Benefits & Incentives",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "compensation, benefits & incentives", "compensation & benefits",
            "compensation and benefits", "compensation", "salary", "annual ctc",
            "base salary", "bonus", "benefits", "equity incentives",
            "stock options", "vesting", "allowances", "remuneration"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "NON_COMPETE": {
        "display": "Non-Compete & Restrictive Covenants",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": [
            "non-compete & restrictive covenants", "non-compete & restraint",
            "non-compete", "non-competition", "covenant not to compete",
            "restrictive covenants", "restraint of trade", "competing business"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CORPORATE_GOVERNANCE"]
    },
    "NON_SOLICITATION": {
        "display": "Non-Solicitation",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "non-solicitation", "non-solicit", "solicitation of clients",
            "solicitation of employees", "no-poach", "employee non-solicitation",
            "customer non-solicitation", "non-solicitation of employees",
            "non-solicitation of customers", "restriction on solicitation"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "CORPORATE_GOVERNANCE"]
    },
    "SEVERANCE_WAIVER": {
        "display": "Severance, Release & Waiver",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "severance, release & waiver", "severance & release", "severance",
            "separation pay", "release of claims", "general release",
            "waiver of claims", "waiver and release", "release and severance"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "COOPERATION_HANDOVER": {
        "display": "Cooperation & Return of Company Property",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "cooperation & return of company property", "executive cooperation",
            "cooperation", "return of company property", "company property in possession",
            "handover of assets", "return of materials", "cooperation and return of property"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA"]
    },

    # --- Property & Real Estate ---
    "PROPERTY_DESCRIPTION": {
        "display": "Property Description & Schedule",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "property description & schedule", "schedule of property", "schedule property",
            "demised premises", "survey number", "khata", "land description"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "TITLE_OWNERSHIP": {
        "display": "Title & Ownership",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": [
            "title & ownership", "marketable title", "absolute owner",
            "chain of title", "ownership rights", "title history", "hereditary rights"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "POSSESSION_REAL_ESTATE": {
        "display": "Possession",
        "dimension": "Operational",
        "default_risk": "medium",
        "aliases": [
            "possession", "vacant possession", "physical possession",
            "handover of possession", "delivery of possession"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "ENCUMBRANCE_MORTGAGE": {
        "display": "Encumbrance & Mortgage",
        "dimension": "Financial",
        "default_risk": "high",
        "aliases": [
            "encumbrance & mortgage", "mortgage", "free from all encumbrances",
            "hypothecation", "court attachment", "lis pendens", "charge on property"
        ],
        "primary_domains": ["REAL_ESTATE", "CORPORATE_GOVERNANCE"]
    },
    "CONSIDERATION_PAYMENT": {
        "display": "Consideration & Payment",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "consideration & payment", "sale consideration", "earnest money",
            "advance token", "balance consideration", "purchase price", "pricing & payment"
        ],
        "primary_domains": ["REAL_ESTATE", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "LEASE_TERM_RENEWAL": {
        "display": "Lease Term & Renewal",
        "dimension": "Legal",
        "default_risk": "medium",
        "aliases": [
            "lease term & renewal", "lease term", "term of lease",
            "ground lease tenure", "lease renewal", "tenancy term"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "SUBLEASE_ASSIGNMENT": {
        "display": "Assignment & Sublease",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": [
            "assignment & sublease", "sublease", "sublet", "subletting",
            "assignment of lease", "prohibition on subleasing"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "PERMITTED_USE_RESTRICTIONS": {
        "display": "Permitted Use & Operational Restrictions",
        "dimension": "Operational",
        "default_risk": "medium",
        "aliases": [
            "permitted use & restrictions", "permitted use", "use of demised premises",
            "operational restrictions", "construction restrictions"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "REGISTRATION_STAMP_DUTY": {
        "display": "Registration & Stamp Duty",
        "dimension": "Compliance",
        "default_risk": "medium",
        "aliases": [
            "registration & stamp duty", "stamp duty", "sub-registrar",
            "registration fee", "stamp paper"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "TAXES_OUTGOINGS": {
        "display": "Taxes & Outgoings",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "taxes & outgoings", "property tax", "betterment charges",
            "municipal taxes", "statutory outgoings"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "DEFAULT_FORFEITURE": {
        "display": "Default & Forfeiture of Earnest Money",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": [
            "default & forfeiture", "earnest money forfeiture",
            "forfeiture of deposit", "specific performance remedies"
        ],
        "primary_domains": ["REAL_ESTATE", "COMMERCIAL_SUPPLY"]
    },

    # --- Confidentiality & IP ---
    "CONFIDENTIALITY_NDA": {
        "display": "Confidentiality & Non-Disclosure",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "confidentiality", "confidentiality & non-disclosure",
            "confidential information", "definition of confidential information",
            "trade secrets", "non-disclosure", "proprietary information",
            "confidentiality and proprietary information"
        ],
        "primary_domains": ["CONFIDENTIALITY_NDA", "EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "IP_ASSIGNMENT": {
        "display": "Intellectual Property Assignment",
        "dimension": "IP",
        "default_risk": "low",
        "aliases": [
            "intellectual property", "intellectual property assignment",
            "ip ownership", "work made for hire", "inventions assignment",
            "inventions and patents", "inventions", "patents", "proprietary rights",
            "intellectual property / inventions / patents"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"]
    },
    "LICENSE_GRANT": {
        "display": "License Grant & Scope",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "license grant & scope", "grant of license", "license scope",
            "authorized users", "permitted seats"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "SLA_SERVICE_LEVEL": {
        "display": "SLA & Uptime Commitments",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "sla & uptime commitments", "service level agreement", "sla",
            "uptime commitment", "service credits"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },

    # --- Privacy & Data Governance ---
    "DATA_PROTECTION_PRIVACY": {
        "display": "Data Protection & Privacy Safeguards",
        "dimension": "Privacy",
        "default_risk": "medium",
        "aliases": [
            "data protection & security", "data protection & privacy",
            "data privacy", "personal data processing", "security safeguards",
            "breach notification"
        ],
        "primary_domains": ["DATA_PRIVACY", "IP_SOFTWARE_TECH", "EMPLOYMENT_LABOR"]
    },

    # --- Universal Commercial Terms ---
    "TERMINATION_NOTICE": {
        "display": "Termination & Notice Period",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "termination", "termination & notice period", "termination and notice period",
            "termination of employment", "employment termination", "termination rights",
            "ending employment", "termination events", "termination and severance",
            "term and termination", "termination for cause", "termination for convenience",
            "notice period"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "REAL_ESTATE"]
    },
    "INDEMNITY_LIABILITY": {
        "display": "Indemnity & Liability",
        "dimension": "Financial",
        "default_risk": "high",
        "aliases": [
            "indemnity & liability", "indemnity", "indemnification",
            "limitation of liability", "liability cap", "consequential damages exclusion",
            "hold harmless"
        ],
        "primary_domains": ["COMMERCIAL_SUPPLY", "IP_SOFTWARE_TECH", "REAL_ESTATE", "CORPORATE_GOVERNANCE", "EMPLOYMENT_LABOR"]
    },
    "GOVERNING_LAW_JURISDICTION": {
        "display": "Governing Law & Jurisdiction",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "governing law & jurisdiction", "governing law and jurisdiction",
            "governing law", "jurisdiction", "applicable law", "choice of law",
            "court jurisdiction"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH", "CORPORATE_GOVERNANCE", "COMMERCIAL_SUPPLY", "DATA_PRIVACY", "GENERAL_COMMERCIAL"]
    },
    "DISPUTE_RESOLUTION_ARBITRATION": {
        "display": "Dispute Resolution & Arbitration",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "dispute resolution & jurisdiction", "dispute resolution & arbitration",
            "arbitration", "dispute resolution", "arbitral seat", "mediation"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH", "CORPORATE_GOVERNANCE", "COMMERCIAL_SUPPLY", "GENERAL_COMMERCIAL"]
    },
    "JURY_TRIAL_WAIVER": {
        "display": "Jury Trial Waiver",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "jury trial waiver", "waiver of jury trial", "jury waiver"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CORPORATE_GOVERNANCE", "COMMERCIAL_SUPPLY", "GENERAL_COMMERCIAL"]
    },
    "SEVERABILITY": {
        "display": "Severability",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "severability", "partial invalidity", "severability of provisions",
            "severability and survival"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH"]
    },
    "COMPLETE_AGREEMENT": {
        "display": "Entire Agreement & Amendments",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "entire agreement", "complete agreement", "integration", "whole agreement",
            "entire agreement & amendments", "amendment and waiver"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH"]
    },
    "REPRESENTATIONS_WARRANTIES": {
        "display": "Representations & Warranties",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "representations & warranties", "reps & warranties", "warranties",
            "covenants and warranties"
        ],
        "primary_domains": ["COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "IP_SOFTWARE_TECH", "REAL_ESTATE"]
    },
    "FORCE_MAJEURE": {
        "display": "Force Majeure",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": ["force majeure", "acts of god", "unforeseen events"],
        "primary_domains": ["COMMERCIAL_SUPPLY", "REAL_ESTATE", "IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL"]
    },
    "NOTICES_COMMUNICATIONS": {
        "display": "Notices & Formal Communications",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "notices & formal communications", "notices", "formal notice",
            "addresses for notice", "notice"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "REAL_ESTATE", "CONFIDENTIALITY_NDA", "EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH"]
    }
}


# ── 2. ALIAS LOOKUP INDEX ───────────────────────────────────────────────────
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for cid, defn in CANONICAL_CLAUSE_DEFINITIONS.items():
    ALIAS_TO_CANONICAL[cid.lower()] = cid
    ALIAS_TO_CANONICAL[defn["display"].lower()] = cid
    for alias in defn["aliases"]:
        ALIAS_TO_CANONICAL[alias.lower().strip()] = cid


def normalize_to_canonical_id(category_or_alias: str) -> Optional[str]:
    """
    Normalizes any string category or alias to its official canonical clause ID.
    """
    if not category_or_alias:
        return None
    clean = category_or_alias.lower().strip()
    
    # Direct lookup
    if clean in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[clean]
        
    # Substring lookup
    for alias, cid in ALIAS_TO_CANONICAL.items():
        if alias in clean or clean in alias:
            return cid
            
    return None
