"""
Clause Intelligence Agent
Performs semantic & deterministic clause extraction across commercial, property, and corporate legal categories.
Includes dedicated real estate / land conveyancing categories (Title, Encumbrance, Mortgage, Possession, Consideration).
"""
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult, AgentFindingModel


class ClauseIntelligenceAgent(BaseAgent):
    RULES = [
        # --- Property & Real Estate Conveyance Categories (High Priority) ---
        {
            "type": "Encumbrance & Mortgage",
            "category": "Encumbrance & Mortgage",
            "risk": "high",
            "dimension": "Financial",
            "keywords": ["mortgage", "mortgaged", "mortgagee", "mortgagor", "hypothecation", "encumbrance", "encumbrances", "free from all encumbrances", "charge", "charges", "lien", "court attachment", "lis pendens", "title deeds deposited"],
            "pattern": r"\b(mortgage|mortgaged|mortgagee|mortgagor|hypothecation|encumbrance|encumbrances|free\s+from\s+all\s+encumbrances|charges?|liens?|court\s+attachment|lis\s+pendens|title\s+deeds\s+deposited)\b"
        },
        {
            "type": "Title & Ownership",
            "category": "Title & Ownership",
            "risk": "high",
            "dimension": "Legal",
            "keywords": ["absolute owner", "marketable title", "clear and marketable title", "chain of title", "hereditary", "ownership rights", "sole and absolute owner"],
            "pattern": r"\b(absolute\s+owner|marketable\s+title|clear\s+and\s+marketable\s+title|chain\s+of\s+title|hereditary|derived\s+title|ownership\s+rights|sole\s+and\s+absolute\s+owner)\b"
        },
        {
            "type": "Possession",
            "category": "Possession",
            "risk": "medium",
            "dimension": "Operational",
            "keywords": ["possession", "vacant possession", "physical possession", "peaceful possession", "hand over possession", "delivery of possession"],
            "pattern": r"\b(vacant\s+possession|physical\s+possession|peaceful\s+possession|hand\s+over\s+possession|delivery\s+of\s+possession|delivered\s+vacant\s+possession|\bpossession\b)\b"
        },
        {
            "type": "Consideration & Payment",
            "category": "Consideration & Payment",
            "risk": "medium",
            "dimension": "Financial",
            "keywords": ["sale consideration", "consideration amount", "advance amount", "advance sum", "balance consideration", "earnest money", "full and final settlement", "payment schedule", "cheque", "neft", "rtgs"],
            "pattern": r"\b(sale\s+consideration|consideration\s+amount|advance\s+amount|advance\s+sum|advance\s+token|balance\s+consideration|earnest\s+money|full\s+and\s+final\s+settlement|payment\s+schedule|demand\s+draft|cheque|rtgs|neft)\b"
        },
        {
            "type": "Registration & Stamp Duty",
            "category": "Registration & Stamp Duty",
            "risk": "medium",
            "dimension": "Compliance",
            "keywords": ["sub-registrar", "stamp duty", "registration charges", "registration fee", "stamp paper", "registration act"],
            "pattern": r"\b(sub[- ]registrar|stamp\s+duty|registration\s+charges|registration\s+fee|stamp\s+paper|duly\s+registered|registration\s+act)\b"
        },
        {
            "type": "Taxes & Outgoings",
            "category": "Taxes & Outgoings",
            "risk": "low",
            "dimension": "Financial",
            "keywords": ["property tax", "betterment charges", "municipal taxes", "electricity dues", "water cess", "statutory dues"],
            "pattern": r"\b(property\s+tax|betterment\s+charges|municipal\s+taxes|electricity\s+(?:dues|charges)|water\s+cess|statutory\s+dues|all\s+taxes\s+and\s+outgoings)\b"
        },
        {
            "type": "Property Description & Schedule",
            "category": "Property Description & Schedule",
            "risk": "low",
            "dimension": "Legal",
            "keywords": ["schedule of property", "schedule property", "survey no", "khata no", "site no", "bounded on", "square feet", "acres", "guntas"],
            "pattern": r"\b(schedule\s+of\s+property|schedule\s+property|survey\s+no|khata\s+no|site\s+no|bounded\s+on\s+the\s+east|bounded\s+on|measuring\s+east\s+to\s+west|square\s+feet|acres|guntas)\b"
        },
        {
            "type": "Default & Forfeiture",
            "category": "Default & Forfeiture",
            "risk": "high",
            "dimension": "Legal",
            "keywords": ["forfeiture", "forfeited", "earnest money forfeited", "specific performance", "time is of the essence"],
            "pattern": r"\b(forfeit|forfeiture|forfeited|earnest\s+money\s+forfeited|breach\s+of\s+contract|specific\s+performance|time\s+is\s+the\s+essence)\b"
        },
        {
            "type": "Sale Restrictions",
            "category": "Sale Restrictions",
            "risk": "high",
            "dimension": "Legal",
            "keywords": ["restriction on sale", "prohibited from selling", "prior consent", "ptcl", "land grant", "clearance certificate"],
            "pattern": r"\b(restriction\s+on\s+sale|prohibited\s+from\s+selling|prior\s+consent\s+of\s+government|ptcl|land\s+grant|clearance\s+certificate|no\s+objection\s+certificate)\b"
        },

        # --- Commercial & General Contract Categories ---
        {
            "type": "Indemnity & Liability",
            "category": "Indemnity & Liability",
            "risk": "high",
            "dimension": "Financial",
            "keywords": ["indemnity", "indemnify", "indemnification", "hold harmless", "unlimited liability", "limitation of liability", "consequential damages", "liquidated damages"],
            "pattern": r"\b(indemnity|indemnify|indemnification|hold\s+harmless|unlimited\s+liability|limitation\s+of\s+liability|consequential\s+damages|liquidated\s+damages)\b"
        },
        {
            "type": "Non-Compete & Restraint",
            "category": "Non-Compete & Restraint",
            "risk": "high",
            "dimension": "Legal",
            "keywords": ["non-compete", "non-competition", "restrictive covenant", "restraint of trade"],
            "pattern": r"\b(non[- ]?compete|non[- ]?competition|restrictive\s+covenant|restraint\s+of\s+trade|covenant\s+not\s+to\s+compete)\b"
        },
        {
            "type": "Non-Solicitation",
            "category": "Non-Solicitation",
            "risk": "medium",
            "dimension": "Operational",
            "keywords": ["non-solicit", "non-solicitation", "solicit employees", "solicit customers"],
            "pattern": r"\b(non[- ]?solicit|non[- ]?solicitation|solicit\s+employees|solicit\s+customers)\b"
        },
        {
            "type": "Termination",
            "category": "Termination",
            "risk": "medium",
            "dimension": "Operational",
            "keywords": ["termination", "terminate", "cancellation", "convenience termination", "material breach"],
            "pattern": r"\b(termination|terminate|terminates|cancellation\s+of\s+agreement|convenience\s+termination|material\s+breach)\b"
        },
        {
            "type": "Confidentiality",
            "category": "Confidentiality",
            "risk": "medium",
            "dimension": "Privacy",
            "keywords": ["confidential", "confidentiality", "non-disclosure", "proprietary information", "trade secret"],
            "pattern": r"\b(confidential|confidentiality|non[- ]?disclosure|proprietary\s+information|trade\s+secret)\b"
        },
        {
            "type": "Dispute Resolution & Arbitration",
            "category": "Dispute Resolution & Arbitration",
            "risk": "medium",
            "dimension": "Legal",
            "keywords": ["arbitration", "mediation", "dispute resolution", "arbitral tribunal", "arbitrator", "seat of arbitration"],
            "pattern": r"\b(arbitration|mediation|dispute\s+resolution|dispute\s+settlement|arbitral\s+tribunal|seat\s+of\s+arbitration|arbitrator)\b"
        },
        {
            "type": "Governing Law & Jurisdiction",
            "category": "Governing Law & Jurisdiction",
            "risk": "low",
            "dimension": "Legal",
            "keywords": ["governing law", "exclusive jurisdiction", "applicable law", "choice of law", "courts at"],
            "pattern": r"\b(governing\s+law|jurisdiction|applicable\s+law|exclusive\s+jurisdiction|choice\s+of\s+law|courts\s+at)\b"
        },
        {
            "type": "Intellectual Property",
            "category": "Intellectual Property",
            "risk": "medium",
            "dimension": "IP",
            "keywords": ["intellectual property", "ip rights", "work for hire", "patent", "copyright", "trademark"],
            "pattern": r"\b(intellectual\s+property|\bip\s+rights\b|work\s+for\s+hire|patent|copyright|trademark|moral\s+rights|assignment\s+of\s+ip)\b"
        },
        {
            "type": "Data Protection & Privacy",
            "category": "Data Protection & Privacy",
            "risk": "high",
            "dimension": "Privacy",
            "keywords": ["personal data", "data protection", "dpdp", "gdpr", "data fiduciary", "data breach"],
            "pattern": r"\b(personal\s+data|data\s+protection|dpdp|gdpr|data\s+fiduciary|data\s+principal|data\s+processor|security\s+safeguards|data\s+breach)\b"
        },
        {
            "type": "Representations & Warranties",
            "category": "Representations & Warranties",
            "risk": "medium",
            "dimension": "Legal",
            "keywords": ["warranties", "representations", "represent and warrant", "as is", "warranty disclaimer"],
            "pattern": r"\b(warranties|representations|represent\s+and\s+warrant|as\s+is|warranty\s+disclaimer|express\s+warranty|implied\s+warranty)\b"
        },
        {
            "type": "Force Majeure",
            "category": "Force Majeure",
            "risk": "low",
            "dimension": "Operational",
            "keywords": ["force majeure", "act of god", "natural disaster", "pandemic", "unforeseen circumstances"],
            "pattern": r"\b(force\s+majeure|act\s+of\s+god|natural\s+disaster|pandemic|epidemic|unforeseen\s+circumstances)\b"
        },
        {
            "type": "Notices & Formal Communications",
            "category": "Notices & Formal Communications",
            "risk": "low",
            "dimension": "Operational",
            "keywords": ["notices under this agreement", "notice address", "registered post", "mode of service of notice"],
            "pattern": r"\b(any\s+notice\s+required|notices\s+under\s+this\s+agreement|served\s+by\s+registered\s+post|notice\s+address|mode\s+of\s+service\s+of\s+notice)\b"
        }
    ]

    def __init__(self):
        super().__init__(
            name="Clause Intelligence Agent",
            description="Extracts and categorizes clauses across 20+ commercial and real estate conveyance categories using semantic pattern matching.",
            capabilities=["clause_extraction", "page_mapping", "category_classification", "property_clause_detection"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        page_texts = context.get("page_texts", [])
        
        # Build page offset map
        page_offsets = []
        if page_texts:
            curr = 0
            for p_num, p_text in enumerate(page_texts, start=1):
                page_offsets.append((curr, p_num))
                curr += len(p_text)
                
        def get_page(pos):
            if not page_offsets: return 1
            pg = 1
            for start, num in page_offsets:
                if pos >= start: pg = num
                else: break
            return pg

        # 1. Segment text into logical blocks / clauses
        # Split by numbered items (e.g. 1. TITLE, Clause 1, Section 1, SCHEDULE) or double newlines
        blocks = []
        raw_splits = re.split(r"(?:\n\s*(?=(?:\d+\.|\bClause\s+\d+|\bSection\s+\d+|\bWHEREAS\b|\bNOW THIS\b|\bSCHEDULE\b)))|\n\s*\n+", text)
        
        curr_offset = 0
        for block in raw_splits:
            clean = block.strip()
            if len(clean) >= 25:
                pos = text.find(clean, curr_offset)
                if pos == -1: pos = curr_offset
                blocks.append((clean, pos))
                curr_offset = pos + len(clean)

        extracted_clauses = []
        findings = []
        seen_contents = set()

        for block_text, pos in blocks:
            lower_block = block_text.lower()
            
            # Score this block against all rules to find the best semantic category
            best_rule = None
            best_score = 0
            
            for rule in self.RULES:
                score = 0
                # Check regex pattern
                if re.search(rule["pattern"], block_text, re.IGNORECASE):
                    score += 3
                # Check keyword hits
                for kw in rule.get("keywords", []):
                    if kw in lower_block:
                        score += 1
                        
                if score > best_score:
                    best_score = score
                    best_rule = rule

            if best_rule and best_score >= 2:
                fp = re.sub(r"\s+", " ", block_text[:60].lower())
                if fp in seen_contents:
                    continue
                seen_contents.add(fp)
                
                page_num = get_page(pos)
                clause_obj = {
                    "type": best_rule["type"],
                    "category": best_rule["category"],
                    "risk": best_rule["risk"],
                    "dimension": best_rule["dimension"],
                    "content": block_text[:350] + "..." if len(block_text) > 350 else block_text,
                    "description": f"{best_rule['type']} clause (Page {page_num})",
                    "page": page_num
                }
                extracted_clauses.append(clause_obj)
                
                risk_score = 85 if best_rule["risk"] == "high" else (50 if best_rule["risk"] == "medium" else 20)
                findings.append(AgentFindingModel(
                    id=f"clause-{len(findings)+1}",
                    agent="Clause Intelligence Agent",
                    dimension=best_rule["dimension"],
                    category=best_rule["category"],
                    severity=best_rule["risk"].upper(),
                    risk_score=risk_score,
                    clause_type=best_rule["type"],
                    clause_text=clause_obj["content"],
                    page_number=page_num,
                    evidence=block_text[:200],
                    claim=f"Identified {best_rule['type']} provision.",
                    reason=f"Clause contains operational terms governing {best_rule['category']}.",
                    recommendation="Review terms to ensure balance of rights and clear risk thresholds.",
                    source_type="DOCUMENT_TEXT",
                    verification_status="TEXT_SUPPORTED",
                    confidence=0.94
                ))

        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=f"Extracted {len(extracted_clauses)} structured clauses across {len(set(c['type'] for c in extracted_clauses))} distinct categories.",
            findings=findings,
            data={"clauses": extracted_clauses, "total_clauses": len(extracted_clauses)}
        )
