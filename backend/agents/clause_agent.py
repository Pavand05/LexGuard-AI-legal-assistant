"""
Clause Intelligence Agent (LexGuard-MA)
Performs domain-weighted, multi-factor semantic clause classification across canonical categories.
Combines:
1. Clause Heading Evidence
2. Active Domain / Document-Type Affinity
3. Positive Semantic Keyword Density
4. Contextual Negative Indicators (e.g. equipment possession vs. real estate possession)
5. Canonical Taxonomy Mapping
"""
import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResult, AgentFindingModel
from .clause_taxonomy import (
    CANONICAL_CLAUSE_DEFINITIONS,
    normalize_to_canonical_id
)
from .playbooks import resolve_domain_playbook, DomainPlaybook


class ClauseIntelligenceAgent(BaseAgent):
    # Candidate classification rules with positive regex patterns and negative context guards
    CANDIDATE_PATTERNS: Dict[str, Dict[str, Any]] = {
        # --- Employment ---
        "POSITION_DUTIES": {
            "patterns": [
                r"\b(position\s+(?:and|&)\s+duties|title\s+(?:and|&)\s+responsibilities|duties\s+(?:and|&)\s+position|reporting\s+to|scope\s+of\s+employment|job\s+title|appointed\s+as|responsibilities\s+of\s+the\s+executive)\b"
            ],
            "negative_patterns": [r"\b(schedule\s+of\s+property|survey\s+no)\b"],
            "headings": ["position", "duties", "responsibilities", "employment", "appointment", "title"]
        },
        "COMPENSATION_BENEFITS": {
            "patterns": [
                r"\b(compensation|base\s+salary|annual\s+ctc|annual\s+salary|bonus\s+plan|equity\s+incentive|stock\s+options?|vesting\s+schedule|fringe\s+benefits|reimbursement\s+of\s+expenses|severance\s+benefit|unvested\s+options?\s+shall\s+be\s+forfeited|clawback)\b"
            ],
            "negative_patterns": [r"\b(sale\s+consideration|advance\s+token|earnest\s+money|sub-registrar)\b"],
            "headings": ["compensation", "salary", "remuneration", "benefits", "equity", "incentives", "bonus"]
        },
        "EMPLOYMENT_TERM": {
            "patterns": [
                r"\b(employment\s+period|period\s+of\s+employment|term\s+of\s+employment|employment\s+term|duration\s+of\s+employment|at-will\s+employment)\b"
            ],
            "negative_patterns": [r"\b(lease\s+term|demised\s+premises|agricultural\s+land|survey\s+no)\b"],
            "headings": ["term", "employment period", "duration", "tenure"]
        },
        "NON_COMPETE": {
            "patterns": [
                r"\b(non[- ]?compete|non[- ]?competition|restrictive\s+covenant|restraint\s+of\s+trade|covenant\s+not\s+to\s+compete|competing\s+business|shall\s+not\s+engage\s+in\s+any\s+competing)\b"
            ],
            "negative_patterns": [],
            "headings": ["non-compete", "restrictive covenants", "competition", "restraint"]
        },
        "NON_SOLICITATION": {
            "patterns": [
                r"\b(non[- ]?solicit|non[- ]?solicitation|solicit\s+employees|solicit\s+customers|induce\s+any\s+employee|solicitation\s+of\s+clients)\b"
            ],
            "negative_patterns": [],
            "headings": ["non-solicitation", "solicitation", "no-poach"]
        },
        "SEVERANCE_WAIVER": {
            "patterns": [
                r"\b(release\s+of\s+claims|general\s+release|waiver\s+and\s+release|severance\s+payment|releases\s+and\s+discharges|claims,\s+charges,\s+demands,\s+and\s+liens|waiver\s+of\s+liability)\b"
            ],
            "negative_patterns": [r"\b(mortgaged\s+with|sub-registrar|survey\s+no)\b"],
            "headings": ["release", "waiver", "severance", "separation", "discharge"]
        },
        "COOPERATION_HANDOVER": {
            "patterns": [
                r"\b(executive\s+cooperation|cooperation\s+clause|return\s+of\s+company\s+property|property\s+in\s+(?:executive|employee)'s\s+possession|return\s+all\s+(?:materials|documents|laptops|keys))\b"
            ],
            "negative_patterns": [r"\b(demised\s+premises|vacant\s+possession\s+of\s+the\s+property|survey\s+no)\b"],
            "headings": ["cooperation", "return of property", "company property", "handover"]
        },

        # --- Property & Real Estate ---
        "PROPERTY_DESCRIPTION": {
            "patterns": [
                r"\b(schedule\s+of\s+property|schedule\s+property|survey\s+no|khata\s+no|site\s+no|bounded\s+on\s+the\s+east|measuring\s+east\s+to\s+west|acres|guntas|square\s+feet)\b"
            ],
            "negative_patterns": [],
            "headings": ["schedule", "description of property", "property details", "demised land"]
        },
        "TITLE_OWNERSHIP": {
            "patterns": [
                r"\b(absolute\s+owner|marketable\s+title|clear\s+and\s+marketable\s+title|chain\s+of\s+title|hereditary\s+ownership|derived\s+title|sole\s+and\s+absolute\s+owner)\b"
            ],
            "negative_patterns": [],
            "headings": ["title", "ownership", "title history", "vendor's title"]
        },
        "POSSESSION_REAL_ESTATE": {
            "patterns": [
                r"\b(vacant\s+possession\s+of\s+(?:the\s+)?(?:property|demised|land|premises)|physical\s+vacant\s+possession|hand\s+over\s+physical\s+possession|delivery\s+of\s+vacant\s+possession)\b"
            ],
            "negative_patterns": [r"\b(in\s+(?:executive|employee)'s\s+possession|company\s+property|laptop)\b"],
            "headings": ["possession", "delivery of possession", "vacant possession"]
        },
        "ENCUMBRANCE_MORTGAGE": {
            "patterns": [
                r"\b(mortgage\s+deed|property\s+was\s+(?:previously\s+)?mortgaged|free\s+from\s+all\s+encumbrances|mortgagee|mortgagor|hypothecation\s+of\s+property|court\s+attachment\s+in\s+os|lis\s+pendens|title\s+deeds\s+deposited)\b"
            ],
            "negative_patterns": [r"\b(claims,\s+charges,\s+demands,\s+and\s+liens\s+against\s+employer|eeoc\s+charges)\b"],
            "headings": ["encumbrance", "mortgage", "charge on property", "court attachment"]
        },
        "CONSIDERATION_PAYMENT": {
            "patterns": [
                r"\b(sale\s+consideration|consideration\s+amount|advance\s+amount|advance\s+sum|advance\s+token|balance\s+consideration|earnest\s+money|full\s+and\s+final\s+settlement\s+of\s+sale|sub-registrar\s+payment)\b"
            ],
            "negative_patterns": [r"\b(annual\s+ctc|base\s+salary|monthly\s+remuneration)\b"],
            "headings": ["consideration", "sale price", "payment terms", "earnest money"]
        },
        "LEASE_TERM_RENEWAL": {
            "patterns": [
                r"\b(lease\s+shall\s+be\s+for\s+a\s+(?:fixed\s+)?term|lease\s+term|term\s+of\s+lease|ground\s+lease\s+period|unilateral\s+right\s+to\s+renew\s+the\s+lease)\b"
            ],
            "negative_patterns": [r"\b(employment\s+agreement|executive\s+employment|annual\s+ctc)\b"],
            "headings": ["lease term", "tenancy period", "lease renewal"]
        },
        "SUBLEASE_ASSIGNMENT": {
            "patterns": [
                r"\b(sublease|sublet|sub-lease|assigning\s+or\s+subleasing|subletting|assignment\s+of\s+lease)\b"
            ],
            "negative_patterns": [],
            "headings": ["sublease", "subletting", "assignment"]
        },
        "PERMITTED_USE_RESTRICTIONS": {
            "patterns": [
                r"\b(permitted\s+use|used\s+solely\s+for|no\s+permanent\s+concrete\s+structures|erect\s+permanent|structures?)\b"
            ],
            "negative_patterns": [],
            "headings": ["permitted use", "use of premises", "construction"]
        },
        "DEFAULT_FORFEITURE": {
            "patterns": [
                r"\b(earnest\s+money\s+(?:shall\s+be\s+)?forfeited|forfeiture\s+of\s+earnest\s+money|forfeiture\s+of\s+security\s+deposit|specific\s+performance\s+of\s+contract|time\s+is\s+of\s+the\s+essence)\b"
            ],
            "negative_patterns": [r"\b(unvested\s+stock\s+options?\s+shall\s+be\s+forfeited|bonus\s+clawback)\b"],
            "headings": ["default", "forfeiture", "failure to complete", "breach & forfeiture"]
        },

        # --- Confidentiality & IP ---
        "CONFIDENTIALITY_NDA": {
            "patterns": [
                r"\b(confidential\s+information|proprietary\s+information|non[- ]?disclosure|trade\s+secrets|standard\s+of\s+care|return\s+or\s+destroy\s+confidential)\b"
            ],
            "negative_patterns": [],
            "headings": ["confidentiality", "non-disclosure", "trade secrets", "proprietary information"]
        },
        "IP_ASSIGNMENT": {
            "patterns": [
                r"\b(intellectual\s+property\s+assignment|inventions?\s+assignment|work\s+(?:made\s+)?for\s+hire|all\s+inventions,\s+patents,\s+and\s+software|proprietary\s+rights|exclusive\s+property\s+of\s+(?:employer|company))\b"
            ],
            "negative_patterns": [],
            "headings": ["intellectual property", "inventions", "ip assignment", "work for hire", "proprietary rights"]
        },
        "LICENSE_GRANT": {
            "patterns": [
                r"\b(grant\s+of\s+license|grants\s+a\s+non-exclusive|licensed\s+software|license\s+scope|permitted\s+named\s+users)\b"
            ],
            "negative_patterns": [],
            "headings": ["license grant", "grant of license", "license scope"]
        },

        # --- Commercial General ---
        "TERMINATION_NOTICE": {
            "patterns": [
                r"\b(termination\s+for\s+cause|termination\s+without\s+cause|written\s+notice\s+of\s+termination|either\s+party\s+may\s+terminate|notice\s+period\s+of\s+\d+\s+days|right\s+to\s+terminate)\b"
            ],
            "negative_patterns": [],
            "headings": ["termination", "notice period", "termination & notice", "separation"]
        },
        "INDEMNITY_LIABILITY": {
            "patterns": [
                r"\b(indemnify\s+(?:and|&)\s+hold\s+harmless|indemnity|limitation\s+of\s+liability|aggregate\s+liability\s+(?:is\s+capped|shall\s+not\s+exceed)|consequential\s+damages\s+exclusion)\b"
            ],
            "negative_patterns": [],
            "headings": ["indemnity", "liability", "limitation of liability", "indemnification"]
        },
        "GOVERNING_LAW_JURISDICTION": {
            "patterns": [
                r"\b(governed\s+by\s+(?:and\s+construed\s+in\s+accordance\s+with\s+)?(?:the\s+)?laws\s+of|exclusive\s+jurisdiction\s+of\s+courts?|subject\s+to\s+(?:the\s+)?jurisdiction\s+of)\b"
            ],
            "negative_patterns": [],
            "headings": ["governing law", "jurisdiction", "applicable law", "choice of law"]
        },
        "DISPUTE_RESOLUTION_ARBITRATION": {
            "patterns": [
                r"\b(arbitration\s+shall\s+be\s+held|arbitral\s+tribunal|dispute\s+resolution\s+mechanism|arbitration\s+seated\s+in|arbitrator)\b"
            ],
            "negative_patterns": [],
            "headings": ["arbitration", "dispute resolution", "arbitral tribunal"]
        }
    }

    def __init__(self):
        super().__init__(
            name="Clause Intelligence Agent",
            description="Extracts and categorizes clauses using domain-weighted multi-factor semantic classification and canonical taxonomy mapping.",
            capabilities=["clause_extraction", "domain_weighted_classification", "canonical_taxonomy_mapping"]
        )

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        text = context.get("text", "")
        doc_type = context.get("document_type", "OTHER_LEGAL_DOCUMENT")
        detected_domains = context.get("detected_domains", ["GENERAL_COMMERCIAL"])
        
        playbook: DomainPlaybook = resolve_domain_playbook(doc_type, detected_domains)
        primary_domain = playbook.domain_name
        
        blocks = self._segment_into_clause_blocks(text)
        clauses: List[Dict[str, Any]] = []
        findings: List[AgentFindingModel] = []
        
        for idx, block in enumerate(blocks):
            heading = block.get("heading", "").strip()
            content = block.get("content", "").strip()
            clean_text = f"{heading}\n{content}".strip()
            lower_block = clean_text.lower()
            
            # Multi-factor score evaluation across candidate canonical categories
            best_cid = None
            best_score = -10.0
            
            for cid, candidate in self.CANDIDATE_PATTERNS.items():
                score = 0.0
                defn = CANONICAL_CLAUSE_DEFINITIONS.get(cid, {})
                primary_domains_for_cid = defn.get("primary_domains", [])
                
                # 1. Heading Evidence
                for h_kw in candidate.get("headings", []):
                    if h_kw in heading.lower():
                        score += 5.0
                        break
                        
                # 2. Domain / Playbook Affinity
                if primary_domain in primary_domains_for_cid:
                    score += 3.0
                elif "REAL_ESTATE" in primary_domains_for_cid and primary_domain == "EMPLOYMENT_LABOR":
                    # Strong negative bias against real estate categories inside employment documents
                    score -= 8.0
                elif "REAL_ESTATE" in primary_domains_for_cid and primary_domain in ["CONFIDENTIALITY_NDA", "IP_SOFTWARE_TECH"]:
                    score -= 6.0
                    
                # 3. Contextual Negative Indicators (Veto triggers)
                has_negative = False
                for neg_pat in candidate.get("negative_patterns", []):
                    if re.search(neg_pat, lower_block, re.IGNORECASE):
                        has_negative = True
                        score -= 10.0
                        break
                        
                if has_negative:
                    continue
                    
                # 4. Positive Regex Pattern Matches
                for pat in candidate.get("patterns", []):
                    matches = list(re.finditer(pat, lower_block, re.IGNORECASE))
                    if matches:
                        score += len(matches) * 3.0
                        
                if score > best_score and score >= 2.0:
                    best_score = score
                    best_cid = cid
                    
            # Fallback if no specific rule met threshold
            if not best_cid:
                # Check if heading gives a clue
                heading_canonical = normalize_to_canonical_id(heading)
                if heading_canonical:
                    best_cid = heading_canonical
                else:
                    best_cid = "NOTICES_COMMUNICATIONS" if "notice" in lower_block else "POSITION_DUTIES" if primary_domain == "EMPLOYMENT_LABOR" and idx == 0 else "GENERAL_PROVISION"

            cid_defn = CANONICAL_CLAUSE_DEFINITIONS.get(best_cid, {
                "display": heading.title() if heading else "General Clause",
                "dimension": "Legal",
                "default_risk": "low"
            })
            
            display_type = cid_defn.get("display", best_cid)
            dimension = cid_defn.get("dimension", "Legal")
            risk = cid_defn.get("default_risk", "low")
            
            clause_obj = {
                "id": f"clause-{idx+1}",
                "canonical_id": best_cid,
                "type": display_type,
                "category": display_type,
                "heading": heading,
                "content": content[:400] if len(content) > 400 else content,
                "full_text": clean_text,
                "page": block.get("page", 1),
                "risk": risk,
                "dimension": dimension,
                "confidence": min(0.96, max(0.60, 0.60 + (best_score * 0.04)))
            }
            clauses.append(clause_obj)
            
            if risk in ["high", "medium"] or best_score >= 4.0:
                findings.append(AgentFindingModel(
                    id=f"clause-finding-{len(findings)+1}",
                    agent="Clause Intelligence Agent",
                    dimension=dimension,
                    category=display_type,
                    severity="HIGH" if risk == "high" else ("MEDIUM" if risk == "medium" else "LOW"),
                    risk_score=75 if risk == "high" else (50 if risk == "medium" else 20),
                    clause_type=display_type,
                    clause_text=content[:250],
                    page_number=block.get("page", 1),
                    evidence=f"Heading: '{heading}' | Canonical: {best_cid} (Score: {best_score:.1f})",
                    claim=f"Identified {display_type} clause under {primary_domain} taxonomy.",
                    reason=f"Structured classification matched canonical category '{best_cid}'.",
                    recommendation="Review terms against standard market benchmarks." if risk in ["high", "medium"] else "Standard operative terms.",
                    source_type="DOCUMENT_TEXT",
                    verification_status="TEXT_SUPPORTED",
                    confidence=clause_obj["confidence"]
                ))

        summary_msg = f"Extracted {len(clauses)} clause block(s) across {len(set(c['canonical_id'] for c in clauses))} canonical categories ({primary_domain} playbook)."
        
        return AgentResult(
            agent_name=self.name,
            status="success",
            confidence=0.94,
            summary=summary_msg,
            findings=findings,
            data={"clauses": clauses, "total_clauses": len(clauses), "primary_domain": primary_domain}
        )

    def _segment_into_clause_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Segments raw text into structured clause units by numbered sections or paragraph headers."""
        blocks: List[Dict[str, Any]] = []
        
        # Regex to detect clause number headings e.g. "1. TITLE:", "  2. MORTGAGE:", "Clause 3:", "SECTION 4. COMPENSATION"
        pattern = r"(?:^|\n)\s*(?:Clause\s+\d+[\.\:]?|\d+[\.\)]|\bSECTION\s+\d+[\.\:]?|\bARTICLE\s+[IVXLCDM\d]+[\.\:]?)\s*([A-Za-z\s&/,\-]{3,60}?)(?::|\n|\.\s+)"
        
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if len(matches) >= 2:
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                heading = matches[i].group(1).strip()
                content = text[start:end].strip()
                blocks.append({"heading": heading, "content": content, "page": 1})
            return blocks
            
        # Paragraph fallback
        paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        if paras:
            for p in paras:
                first_line = p.split("\n")[0][:60]
                blocks.append({"heading": first_line, "content": p, "page": 1})
            return blocks
            
        return [{"heading": "General Document Body", "content": text, "page": 1}]
