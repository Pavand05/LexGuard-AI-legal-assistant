"""
Canonical Clause Taxonomy & Domain Compatibility Matrix (LexGuard-MA)
Defines shared canonical clause identifiers, category aliases, descriptions,
and domain compatibility affinities across legal domains including SaaS, Commercial, Real Estate, and Employment.
"""
from typing import Dict, Any, List, Set, Optional


# ── 1. CANONICAL CLAUSE DEFINITIONS ──────────────────────────────────────────
CANONICAL_CLAUSE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # --- SaaS, Cloud, Software & Technology ---
    "SERVICE_SCOPE": {
        "display": "Service Scope & Platform Access",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "service scope", "scope of services", "platform access", "services description",
            "cloud services", "service provision", "saas scope", "platform services"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"]
    },
    "HOSTING_MAINTENANCE": {
        "display": "Hosting, Maintenance & Availability",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "hosting", "maintenance", "platform maintenance", "server hosting",
            "cloud hosting", "system availability", "scheduled maintenance", "updates and upgrades"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "SOFTWARE_LICENSE": {
        "display": "Software License Grant & Scope",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "license grant & scope", "grant of license", "software license", "license scope",
            "authorized users", "permitted seats", "license grant", "api license"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "LICENSE_GRANT": {
        "display": "Software License Grant & Scope",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "license grant & scope", "grant of license", "license scope", "authorized users"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "IP_OWNERSHIP": {
        "display": "Intellectual Property Ownership & Reservation of Rights",
        "dimension": "IP",
        "default_risk": "low",
        "aliases": [
            "intellectual property", "ip ownership", "reservation of rights", "proprietary rights",
            "ownership of platform", "intellectual property rights", "company ip"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "EMPLOYMENT_LABOR", "COMMERCIAL_SUPPLY"]
    },
    "IP_ASSIGNMENT": {
        "display": "Intellectual Property Assignment",
        "dimension": "IP",
        "default_risk": "low",
        "aliases": [
            "intellectual property assignment", "inventions assignment", "work made for hire",
            "patent assignment", "inventions", "patents"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"]
    },
    "IP_RESTRICTIONS": {
        "display": "IP Restrictions & Reverse Engineering Prohibitions",
        "dimension": "IP",
        "default_risk": "low",
        "aliases": [
            "ip restrictions", "reverse engineering", "restrictions on use", "license restrictions",
            "decompilation", "disassembly", "prohibited use"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "SLA_SERVICE_LEVEL": {
        "display": "SLA & Uptime Commitments",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "sla & uptime commitments", "service level agreement", "sla", "uptime commitment",
            "service credits", "performance standards", "uptime guarantee"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "SUPPORT_SERVICES": {
        "display": "Technical Support & Error Correction",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "technical support", "support services", "error correction", "helpdesk",
            "bug fixes", "maintenance and support", "support tier"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH"]
    },
    "FEES_PAYMENT": {
        "display": "Fees, Pricing & Payment Terms",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "fees", "pricing & payment", "payment terms", "subscription fees", "service fees",
            "invoicing and payment", "billing", "charges and fees", "fees and payment"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "GENERAL_COMMERCIAL"]
    },
    "REVENUE_SHARE": {
        "display": "Revenue Sharing & Distribution Royalties",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "revenue share", "revenue sharing", "royalty payments", "distribution share",
            "monetization split", "net revenue share", "revenue share payment"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "FINANCIAL_AUDIT": {
        "display": "Financial Audit & Inspection Rights",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "audit rights", "financial audit", "books and records", "inspection of accounts",
            "right to audit", "audit and inspection", "accounting records"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "TAXES_FEES": {
        "display": "Taxes & Withholding Obligations",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "taxes", "tax obligations", "withholding taxes", "sales tax", "indirect taxes",
            "value added tax", "goods and services tax"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "REAL_ESTATE"]
    },
    "DATA_SECURITY": {
        "display": "Data Security & Customer Data Safeguards",
        "dimension": "Privacy",
        "default_risk": "medium",
        "aliases": [
            "data security", "customer data", "subscriber data", "security safeguards",
            "data protection & privacy", "data privacy", "data safeguards", "data breach"
        ],
        "primary_domains": ["DATA_PRIVACY", "IP_SOFTWARE_TECH", "EMPLOYMENT_LABOR"]
    },
    "DATA_PROTECTION_PRIVACY": {
        "display": "Data Protection & Privacy Safeguards",
        "dimension": "Privacy",
        "default_risk": "medium",
        "aliases": [
            "data protection & security", "data protection & privacy", "data privacy",
            "personal data processing", "security safeguards", "breach notification"
        ],
        "primary_domains": ["DATA_PRIVACY", "IP_SOFTWARE_TECH", "EMPLOYMENT_LABOR"]
    },
    "INSURANCE": {
        "display": "Insurance Requirements & Coverage",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "insurance", "insurance requirements", "cyber liability insurance",
            "commercial general liability", "errors and omissions", "workers compensation"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "REAL_ESTATE"]
    },
    "PUBLICITY": {
        "display": "Publicity & Press Release Restrictions",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "publicity", "press releases", "marketing materials", "use of name and logo",
            "public announcements", "trademarks and logos"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "CONFIDENTIALITY_NDA", "COMMERCIAL_SUPPLY"]
    },
    "EXPORT_COMPLIANCE": {
        "display": "Export Controls & Sanctions Compliance",
        "dimension": "Compliance",
        "default_risk": "low",
        "aliases": [
            "export compliance", "export controls", "sanctions", "ear compliance",
            "trade restrictions", "ofac", "regulatory approvals"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY"]
    },

    # --- Confidentiality & Restrictive Terms ---
    "CONFIDENTIALITY_NDA": {
        "display": "Confidentiality & Non-Disclosure",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "confidentiality", "confidentiality & non-disclosure", "confidential information",
            "definition of confidential information", "trade secrets", "non-disclosure",
            "proprietary information", "confidentiality and proprietary information"
        ],
        "primary_domains": ["CONFIDENTIALITY_NDA", "EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "NON_COMPETE": {
        "display": "Non-Compete & Restrictive Covenants",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": [
            "non-compete & restrictive covenants", "non-compete & restraint", "non-compete",
            "non-competition", "covenant not to compete", "restrictive covenants", "restraint of trade"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CORPORATE_GOVERNANCE"]
    },
    "NON_SOLICITATION": {
        "display": "Non-Solicitation",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "non-solicitation", "non-solicit", "solicitation of clients", "solicitation of employees",
            "no-poach", "employee non-solicitation", "customer non-solicitation"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "CORPORATE_GOVERNANCE"]
    },

    # --- Liability & Indemnification ---
    "INDEMNITY_LIABILITY": {
        "display": "Indemnity & Liability",
        "dimension": "Financial",
        "default_risk": "high",
        "aliases": [
            "indemnity & liability", "indemnity", "indemnification", "limitation of liability",
            "liability cap", "consequential damages exclusion", "hold harmless"
        ],
        "primary_domains": ["COMMERCIAL_SUPPLY", "IP_SOFTWARE_TECH", "REAL_ESTATE", "CORPORATE_GOVERNANCE", "EMPLOYMENT_LABOR"]
    },
    "INDEMNIFICATION": {
        "display": "Indemnification & Defense Obligations",
        "dimension": "Financial",
        "default_risk": "high",
        "aliases": [
            "indemnification", "indemnity", "defense obligations", "hold harmless",
            "ip infringement indemnity", "indemnification procedures"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "REAL_ESTATE", "CORPORATE_GOVERNANCE", "EMPLOYMENT_LABOR"]
    },
    "LIABILITY_LIMITATION": {
        "display": "Limitation of Liability & Damages Waiver",
        "dimension": "Financial",
        "default_risk": "medium",
        "aliases": [
            "limitation of liability", "liability limitations", "liability cap",
            "exclusion of consequential damages", "waiver of indirect damages", "aggregate liability"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "GENERAL_COMMERCIAL"]
    },

    # --- Term, Termination & Survival ---
    "TERMINATION_NOTICE": {
        "display": "Termination & Notice Period",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "termination", "termination & notice period", "termination and notice period",
            "termination of employment", "employment termination", "termination rights",
            "term and termination", "termination for cause", "termination for convenience",
            "notice period", "termination and cure period"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "REAL_ESTATE"]
    },
    "SURVIVAL": {
        "display": "Survival of Provisions",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "survival", "survival of provisions", "surviving provisions", "survival of terms"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "GENERAL_COMMERCIAL"]
    },

    # --- Governing Law, Jurisdiction & Dispute Resolution ---
    "GOVERNING_LAW_JURISDICTION": {
        "display": "Governing Law & Jurisdiction",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "governing law & jurisdiction", "governing law and jurisdiction", "governing law",
            "jurisdiction", "applicable law", "choice of law", "court jurisdiction",
            "governing law and venue"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH", "CORPORATE_GOVERNANCE", "COMMERCIAL_SUPPLY", "DATA_PRIVACY", "GENERAL_COMMERCIAL"]
    },
    "GOVERNING_LAW": {
        "display": "Governing Law",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "governing law", "applicable law", "choice of law", "controlling law"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA"]
    },
    "COURT_JURISDICTION": {
        "display": "Court Jurisdiction & Venue",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "court jurisdiction", "venue", "exclusive jurisdiction", "court venue", "forum selection"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA"]
    },
    "DISPUTE_RESOLUTION_ARBITRATION": {
        "display": "Dispute Resolution & Arbitration",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "dispute resolution & jurisdiction", "dispute resolution & arbitration", "arbitration",
            "dispute resolution", "arbitral seat", "mediation"
        ],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH", "CORPORATE_GOVERNANCE", "COMMERCIAL_SUPPLY", "GENERAL_COMMERCIAL"]
    },
    "ARBITRATION": {
        "display": "Arbitration",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "arbitration", "arbitral tribunal", "arbitration proceedings", "binding arbitration"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL", "CORPORATE_GOVERNANCE"]
    },

    # --- Boilerplate ---
    "ASSIGNMENT_SUBCONTRACTING": {
        "display": "Assignment & Subcontracting",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "assignment", "subcontracting", "assignment and subcontracting", "successors and assigns"
        ],
        "primary_domains": ["IP_SOFTWARE_TECH", "COMMERCIAL_SUPPLY", "GENERAL_COMMERCIAL"]
    },
    "NOTICES_COMMUNICATIONS": {
        "display": "Notices & Formal Communications",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": [
            "notices & formal communications", "notices", "formal notice", "addresses for notice"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "REAL_ESTATE", "CONFIDENTIALITY_NDA", "EMPLOYMENT_LABOR", "IP_SOFTWARE_TECH"]
    },
    "SEVERABILITY": {
        "display": "Severability",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "severability", "partial invalidity", "severability of provisions"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH"]
    },
    "COMPLETE_AGREEMENT": {
        "display": "Entire Agreement & Amendments",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "entire agreement", "complete agreement", "integration", "whole agreement",
            "entire agreement & amendments", "amendments", "modification"
        ],
        "primary_domains": ["GENERAL_COMMERCIAL", "EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "REAL_ESTATE", "IP_SOFTWARE_TECH"]
    },
    "FORCE_MAJEURE": {
        "display": "Force Majeure",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": ["force majeure", "acts of god", "unforeseen events"],
        "primary_domains": ["COMMERCIAL_SUPPLY", "REAL_ESTATE", "IP_SOFTWARE_TECH", "GENERAL_COMMERCIAL"]
    },
    "REPRESENTATIONS_WARRANTIES": {
        "display": "Representations & Warranties",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": [
            "representations & warranties", "reps & warranties", "warranties", "covenants and warranties"
        ],
        "primary_domains": ["COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE", "IP_SOFTWARE_TECH", "REAL_ESTATE"]
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

    # --- Real Estate ---
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
            "title & ownership", "marketable title", "absolute owner", "chain of title"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "POSSESSION_REAL_ESTATE": {
        "display": "Possession",
        "dimension": "Operational",
        "default_risk": "medium",
        "aliases": [
            "possession", "vacant possession", "physical possession", "handover of possession"
        ],
        "primary_domains": ["REAL_ESTATE"]
    },
    "ENCUMBRANCE_MORTGAGE": {
        "display": "Encumbrance & Mortgage",
        "dimension": "Financial",
        "default_risk": "high",
        "aliases": [
            "encumbrance & mortgage", "mortgage", "free from all encumbrances", "hypothecation"
        ],
        "primary_domains": ["REAL_ESTATE", "CORPORATE_GOVERNANCE"]
    },
    "CONSIDERATION_PAYMENT": {
        "display": "Consideration & Payment",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": [
            "consideration & payment", "sale consideration", "earnest money", "advance token", "purchase price"
        ],
        "primary_domains": ["REAL_ESTATE", "COMMERCIAL_SUPPLY", "CORPORATE_GOVERNANCE"]
    },
    "LEASE_TERM_RENEWAL": {
        "display": "Lease Term & Renewal",
        "dimension": "Legal",
        "default_risk": "medium",
        "aliases": ["lease term & renewal", "lease term", "term of lease", "ground lease tenure"],
        "primary_domains": ["REAL_ESTATE"]
    },
    "SUBLEASE_ASSIGNMENT": {
        "display": "Assignment & Sublease",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": ["assignment & sublease", "sublease", "sublet", "assignment of lease"],
        "primary_domains": ["REAL_ESTATE"]
    },
    "PERMITTED_USE_RESTRICTIONS": {
        "display": "Permitted Use & Operational Restrictions",
        "dimension": "Operational",
        "default_risk": "medium",
        "aliases": ["permitted use & restrictions", "permitted use", "operational restrictions"],
        "primary_domains": ["REAL_ESTATE"]
    },
    "REGISTRATION_STAMP_DUTY": {
        "display": "Registration & Stamp Duty",
        "dimension": "Compliance",
        "default_risk": "medium",
        "aliases": ["registration & stamp duty", "stamp duty", "sub-registrar"],
        "primary_domains": ["REAL_ESTATE"]
    },
    "TAXES_OUTGOINGS": {
        "display": "Taxes & Outgoings",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": ["taxes & outgoings", "property tax", "betterment charges"],
        "primary_domains": ["REAL_ESTATE"]
    },
    "DEFAULT_FORFEITURE": {
        "display": "Default & Forfeiture of Earnest Money",
        "dimension": "Legal",
        "default_risk": "high",
        "aliases": ["default & forfeiture", "earnest money forfeiture", "forfeiture of deposit"],
        "primary_domains": ["REAL_ESTATE", "COMMERCIAL_SUPPLY"]
    },

    # --- Employment ---
    "EMPLOYMENT_TERM": {
        "display": "Employment Term & Tenure",
        "dimension": "Legal",
        "default_risk": "low",
        "aliases": ["employment term", "period of employment", "employment period", "term of employment"],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "POSITION_DUTIES": {
        "display": "Position, Duties & Scope",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": ["position, duties & scope", "position and duties", "duties & position", "job title"],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "COMPENSATION_BENEFITS": {
        "display": "Compensation, Benefits & Incentives",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": ["compensation, benefits & incentives", "compensation & benefits", "base salary", "annual ctc"],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "SEVERANCE_WAIVER": {
        "display": "Severance, Release & Waiver",
        "dimension": "Financial",
        "default_risk": "low",
        "aliases": ["severance, release & waiver", "severance & release", "release of claims", "general release"],
        "primary_domains": ["EMPLOYMENT_LABOR"]
    },
    "COOPERATION_HANDOVER": {
        "display": "Cooperation & Return of Company Property",
        "dimension": "Operational",
        "default_risk": "low",
        "aliases": ["cooperation & return of company property", "executive cooperation", "return of company property"],
        "primary_domains": ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA"]
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
