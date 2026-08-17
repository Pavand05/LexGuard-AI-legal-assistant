"""
Clause Intelligence Agent (LexGuard-MA)
Performs domain-weighted, multi-factor semantic clause classification across canonical categories.
Implements universal Evidence <-> Canonical Category Compatibility:
- Prevents "termination of discussions" from triggering contract termination
- Prevents "limited liability company" from triggering liability covenants
- Prevents recurring terms ("Evaluation Material") from hijacking Termination/Liability/Jurisdiction headings
- Prevents incidental notification ("notify disclosing party of breach") from triggering formal notice clauses
- Segmenting numbered and decimal sections, as well as SCHEDULE/EXHIBIT/APPENDIX blocks
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
    CANDIDATE_PATTERNS: Dict[str, Dict[str, Any]] = {
        # --- Termination ---
        "TERMINATION_NOTICE": {
            "patterns": [
                r"\b(term\s+of\s+this\s+agreement\s+shall\s+expire|this\s+agreement\s+shall\s+terminate|either\s+party\s+may\s+terminate\s+this\s+agreement|terminate\s+this\s+agreement\s+upon|termination\s+for\s+cause|termination\s+without\s+cause|written\s+notice\s+of\s+termination|notice\s+period\s+of\s+\d+\s+days|termination\s+of\s+employment|employment\s+termination|shall\s+terminate\s+(?:upon\s+the\s+earlier\s+of|on\s+the\s+second|after\s+\d+\s+years))\b"
            ],
            "negative_patterns": [
                r"\b(termination\s+of\s+(?:discussions|negotiations|talks|evaluations)|prior\s+to\s+(?:the\s+)?termination\s+of\s+discussions)\b"
            ],
            "headings": ["termination", "term and termination", "term", "notice period", "termination & notice", "termination of employment", "employment termination", "termination and notice period", "duration"]
        },

        # --- Indemnity & Liability ---
        "INDEMNITY_LIABILITY": {
            "patterns": [
                r"\b(indemnify\s+(?:and|&)\s+hold\s+harmless|indemnification|limitation\s+of\s+liability|aggregate\s+liability\s+(?:is\s+capped|shall\s+not\s+exceed)|consequential\s+damages\s+exclusion|neither\s+party\s+shall\s+have\s+any\s+liability|neither\s+party\s+shall\s+be\s+liable|no\s+liability\s+for\s+(?:punitive|indirect|special|consequential)|disclaimer\s+of\s+warranties\s+(?:and\s+limitation\s+of\s+liability|and\s+liability))\b"
            ],
            "negative_patterns": [
                r"\b(limited\s+liability\s+(?:company|partnership)|a\s+delaware\s+limited\s+liability\s+company|a\s+california\s+limited\s+liability)\b"
            ],
            "headings": ["indemnity", "liability", "limitation of liability", "indemnification", "disclaimer of liability", "damages disclaimer", "remedies and liability", "disclaimer of warranties and limitation of liability", "disclaimer of warranties"]
        },

        # --- Governing Law & Jurisdiction ---
        "GOVERNING_LAW_JURISDICTION": {
            "patterns": [
                r"\b(governed\s+by\s+(?:and\s+construed\s+in\s+accordance\s+with\s+)?(?:the\s+)?(?:internal\s+)?laws\s+of|exclusive\s+jurisdiction\s+of\s+(?:the\s+)?(?:Court\s+of\s+Chancery|state\s+and\s+federal\s+)?courts?|subject\s+to\s+(?:the\s+)?jurisdiction\s+of\s+courts?|state\s+and\s+federal\s+courts\s+located\s+in|choice\s+of\s+law|exclusive\s+jurisdiction\s+and\s+venue)\b"
            ],
            "negative_patterns": [],
            "headings": ["governing law", "jurisdiction", "applicable law", "choice of law", "governing law and jurisdiction", "jurisdiction and venue", "exclusive jurisdiction and venue", "venue"]
        },

        # --- Dispute Resolution & Arbitration ---
        "DISPUTE_RESOLUTION_ARBITRATION": {
            "patterns": [
                r"\b(arbitration\s+shall\s+be\s+held|arbitral\s+tribunal|dispute\s+resolution\s+mechanism|arbitration\s+seated\s+in|arbitrator|rules\s+of\s+arbitration\s+of)\b"
            ],
            "negative_patterns": [],
            "headings": ["arbitration", "dispute resolution", "arbitral tribunal", "mediation and arbitration"]
        },

        # --- Non-Solicitation ---
        "NON_SOLICITATION": {
            "patterns": [
                r"\b(non[- ]?solicit|non[- ]?solicitation|solicit\s+employees|solicit\s+customers|induce\s+any\s+employee|solicitation\s+of\s+clients|shall\s+not\s+solicit\s+any|employee\s+non-solicitation|customer\s+non-solicitation|solicitation\s+of\s+employees|solicit,\s+recruit,\s+or\s+hire|solicit\s+or\s+divert\s+any\s+employee)\b"
            ],
            "negative_patterns": [],
            "headings": ["non-solicitation", "non-solicit", "solicitation", "no-poach", "employee non-solicitation", "customer non-solicitation", "non-solicitation of employees"]
        },

        # --- Non-Compete ---
        "NON_COMPETE": {
            "patterns": [
                r"\b(non[- ]?compete|non[- ]?competition|restrictive\s+covenant|restraint\s+of\s+trade|covenant\s+not\s+to\s+compete|competing\s+business|shall\s+not\s+engage\s+in\s+any\s+competing)\b"
            ],
            "negative_patterns": [],
            "headings": ["non-compete", "restrictive covenants", "competition", "restraint", "covenant not to compete"]
        },

        # --- Formal Notices & Communications ---
        "NOTICES_COMMUNICATIONS": {
            "patterns": [
                r"\b(all\s+notices\s+(?:under\s+this\s+Agreement\s+)?shall\s+be\s+in\s+writing\s+and\s+shall\s+be\s+deemed\s+(?:to\s+have\s+been\s+)?given|notices\s+shall\s+be\s+delivered\s+to\s+the\s+addresses\s+set\s+forth|notices\s+hereunder\s+shall\s+be\s+sent\s+by\s+(?:certified\s+mail|overnight\s+courier|email)|addresses\s+for\s+notice)\b"
            ],
            "negative_patterns": [
                r"\b(?:notify\s+the\s+disclosing\s+party\s+in\s+writing\s+(?:immediately|prior\s+to\s+disclosure|of\s+any\s+breach))\b"
            ],
            "headings": ["notices", "formal notices", "notices and formal communications", "addresses for notice"]
        },

        # --- Confidentiality & NDA ---
        "CONFIDENTIALITY_NDA": {
            "patterns": [
                r"\b(confidential\s+information|proprietary\s+information|non[- ]?disclosure|trade\s+secrets|standard\s+of\s+care|return\s+or\s+destroy\s+confidential|maintain\s+in\s+strict\s+confidence|evaluation\s+material|transaction\s+information|compelled\s+disclosure)\b"
            ],
            "negative_patterns": [],
            "headings": ["confidentiality", "non-disclosure", "trade secrets", "proprietary information", "confidential information", "definition of confidential information", "definitions and evaluation material", "confidentiality and standard of care", "compelled disclosure"]
        },

        # --- Real Estate ---
        "PROPERTY_DESCRIPTION": {
            "patterns": [
                r"\b(schedule\s+of\s+property|schedule\s+property|survey\s+no|khata\s+no|site\s+no|residential\s+site\s+no|bounded\s+on\s+the\s+east|measuring\s+east\s+to\s+west|acres|guntas|square\s+feet|all\s+that\s+piece\s+and\s+parcel)\b"
            ],
            "negative_patterns": [],
            "headings": ["schedule", "schedule of property", "description of property", "property details", "demised land", "schedule property"]
        },
        "TITLE_OWNERSHIP": {
            "patterns": [
                r"\b(absolute\s+owner|marketable\s+title|clear\s+and\s+marketable\s+title|chain\s+of\s+title|hereditary\s+ownership|derived\s+title|sole\s+and\s+absolute\s+owner)\b"
            ],
            "negative_patterns": [],
            "headings": ["title", "ownership", "title history", "vendor's title", "title and ownership"]
        },
        "POSSESSION_REAL_ESTATE": {
            "patterns": [
                r"\b(vacant\s+possession\s+of\s+(?:the\s+)?(?:property|demised|land|premises)|physical\s+vacant\s+possession|hand\s+over\s+physical\s+possession|delivery\s+of\s+vacant\s+possession|possession\s+status)\b"
            ],
            "negative_patterns": [r"\b(in\s+(?:executive|employee)'s\s+possession|company\s+property|laptop)\b"],
            "headings": ["possession", "delivery of possession", "vacant possession", "possession status recital"]
        },
        "ENCUMBRANCE_MORTGAGE": {
            "patterns": [
                r"\b(mortgage\s+deed|property\s+was\s+(?:previously\s+)?mortgaged|free\s+from\s+all\s+encumbrances|mortgagee|mortgagor|hypothecation\s+of\s+property|court\s+attachment\s+in\s+os|lis\s+pendens|title\s+deeds\s+deposited)\b"
            ],
            "negative_patterns": [r"\b(claims,\s+charges,\s+demands,\s+and\s+liens\s+against\s+employer|eeoc\s+charges)\b"],
            "headings": ["encumbrance", "mortgage", "charge on property", "court attachment", "encumbrance and mortgage"]
        },
        "CONSIDERATION_PAYMENT": {
            "patterns": [
                r"\b(sale\s+consideration|consideration\s+amount|advance\s+amount|advance\s+sum|advance\s+token|balance\s+consideration|earnest\s+money|full\s+and\s+final\s+settlement\s+of\s+sale|sub-registrar\s+payment|receipt\s+of\s+full\s+consideration)\b"
            ],
            "negative_patterns": [r"\b(annual\s+ctc|base\s+salary|monthly\s+remuneration)\b"],
            "headings": ["consideration", "sale price", "payment terms", "earnest money", "sale consideration and payment", "receipt of full consideration"]
        },
        "REGISTRATION_STAMP_DUTY": {
            "patterns": [
                r"\b(stamp\s+duty|registration\s+charges|sub-registrar\s+office|duly\s+stamped\s+and\s+registered|registration\s+fee)\b"
            ],
            "negative_patterns": [],
            "headings": ["registration and stamp duty", "stamp duty", "registration"]
        },
        "TAXES_OUTGOINGS": {
            "patterns": [
                r"\b(property\s+tax|municipal\s+taxes|betterment\s+charges|statutory\s+outgoings|electricity\s+and\s+water\s+charges)\b"
            ],
            "negative_patterns": [],
            "headings": ["taxes and outgoings", "property taxes", "outgoings"]
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

        # --- Employment Terms ---
        "POSITION_DUTIES": {
            "patterns": [
                r"\b(position\s+(?:and|&)\s+duties|title\s+(?:and|&)\s+responsibilities|duties\s+(?:and|&)\s+position|reporting\s+to|scope\s+of\s+employment|job\s+title|appointed\s+as|responsibilities\s+of\s+the\s+executive|serve\s+as\s+[A-Za-z\s]+reporting)\b"
            ],
            "negative_patterns": [r"\b(schedule\s+of\s+property|survey\s+no)\b"],
            "headings": ["position", "duties", "responsibilities", "employment", "appointment", "title", "position and duties", "scope of duties"]
        },
        "COMPENSATION_BENEFITS": {
            "patterns": [
                r"\b(compensation|base\s+salary|annual\s+ctc|annual\s+salary|bonus\s+plan|equity\s+incentive|stock\s+options?|vesting\s+schedule|fringe\s+benefits|reimbursement\s+of\s+expenses|severance\s+benefit|clawback|annualized\s+base\s+salary)\b"
            ],
            "negative_patterns": [r"\b(sale\s+consideration|advance\s+token|earnest\s+money|sub-registrar)\b"],
            "headings": ["compensation", "salary", "remuneration", "benefits", "equity", "incentives", "bonus", "compensation and benefits"]
        },
        "EMPLOYMENT_TERM": {
            "patterns": [
                r"\b(period\s+of\s+employment|employment\s+period|term\s+of\s+employment|employment\s+term|duration\s+of\s+employment|at-will\s+employment|initial\s+fixed\s+term\s+of\s+\d+|commencing\s+on\s+the\s+effective\s+date|employs\s+executive[^\n.]+initial\s+term)\b"
            ],
            "negative_patterns": [
                r"\b(lease\s+term|demised\s+premises|agricultural\s+land|survey\s+no)\b",
                r"\b(?:section\s+\d+\s+shall\s+survive|survives\s+termination\s+of\s+the\s+employment\s+period)\b"
            ],
            "headings": ["term", "employment period", "duration", "tenure", "period of employment", "employment term"]
        },
        "SEVERANCE_WAIVER": {
            "patterns": [
                r"\b(release\s+of\s+claims|general\s+release|waiver\s+and\s+release|severance\s+payment|releases\s+and\s+discharges|claims,\s+charges,\s+demands,\s+and\s+liens|waiver\s+of\s+liability|separation\s+release|in\s+exchange\s+for\s+severance)\b"
            ],
            "negative_patterns": [r"\b(mortgaged\s+with|sub-registrar|survey\s+no)\b"],
            "headings": ["release", "waiver", "severance", "separation", "discharge", "release and severance", "severance and release"]
        },
        "COOPERATION_HANDOVER": {
            "patterns": [
                r"\b(executive\s+cooperation|cooperation\s+clause|return\s+of\s+company\s+property|property\s+in\s+(?:executive|employee)'s\s+possession|return\s+all\s+(?:materials|documents|laptops|keys)|cooperation\s+and\s+return\s+of\s+property)\b"
            ],
            "negative_patterns": [r"\b(demised\s+premises|vacant\s+possession\s+of\s+the\s+property|survey\s+no)\b"],
            "headings": ["cooperation", "return of property", "company property", "handover", "executive cooperation"]
        },

        # --- Intellectual Property ---
        "IP_ASSIGNMENT": {
            "patterns": [
                r"\b(intellectual\s+property\s+assignment|inventions?\s+assignment|work\s+(?:made\s+)?for\s+hire|all\s+inventions,\s+software,\s+patents|proprietary\s+rights|exclusive\s+property\s+of\s+(?:employer|company)|works\s+of\s+authorship)\b"
            ],
            "negative_patterns": [],
            "headings": ["intellectual property", "inventions", "ip assignment", "work for hire", "proprietary rights", "patents", "inventions and patents"]
        },

        # --- General Commercial Boilerplate ---
        "JURY_TRIAL_WAIVER": {
            "patterns": [
                r"\b(waiver\s+of\s+jury\s+trial|jury\s+trial\s+waiver|waives?\s+(?:all\s+)?right\s+to\s+a\s+jury\s+trial|waive\s+any\s+right\s+to\s+jury\s+trial)\b"
            ],
            "negative_patterns": [],
            "headings": ["jury trial waiver", "waiver of jury trial", "jury waiver"]
        },
        "SEVERABILITY": {
            "patterns": [
                r"\b(severability|severable|invalidity\s+of\s+any\s+provision|held\s+to\s+be\s+invalid\s+or\s+unenforceable)\b"
            ],
            "negative_patterns": [],
            "headings": ["severability", "partial invalidity", "severability of provisions"]
        },
        "COMPLETE_AGREEMENT": {
            "patterns": [
                r"\b(entire\s+agreement|complete\s+understanding|supersedes\s+all\s+prior|complete\s+agreement|entire\s+agreement\s+and\s+amendments)\b"
            ],
            "negative_patterns": [],
            "headings": ["entire agreement", "complete agreement", "integration", "whole agreement"]
        }
    }

    def __init__(self):
        super().__init__(
            name="Clause Intelligence Agent",
            description="Extracts and categorizes clauses using domain-weighted multi-factor semantic classification and canonical taxonomy mapping.",
            capabilities=["clause_extraction", "domain_weighted_classification", "canonical_taxonomy_mapping", "evidence_grounding", "compatibility_validation"]
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
            lower_heading = heading.lower()
            
            best_cid = None
            best_score = -10.0
            best_evidence = content[:200]
            
            for cid, candidate in self.CANDIDATE_PATTERNS.items():
                score = 0.0
                defn = CANONICAL_CLAUSE_DEFINITIONS.get(cid, {})
                primary_domains_for_cid = defn.get("primary_domains", [])
                
                # 1. Contextual Negative Indicators (Strict Compatibility Veto)
                has_negative = False
                for neg_pat in candidate.get("negative_patterns", []):
                    if re.search(neg_pat, lower_block, re.IGNORECASE):
                        has_negative = True
                        break
                        
                if has_negative:
                    continue

                # 2. Heading Evidence (Heavy weighting for explicit headings)
                heading_matched = False
                for h_kw in candidate.get("headings", []):
                    if h_kw in lower_heading:
                        score += 12.0
                        heading_matched = True
                        break
                        
                # 3. Domain / Playbook Affinity
                if primary_domain in primary_domains_for_cid:
                    score += 3.0
                elif "REAL_ESTATE" in primary_domains_for_cid and primary_domain in ["EMPLOYMENT_LABOR", "CONFIDENTIALITY_NDA", "IP_SOFTWARE_TECH"]:
                    score -= 10.0
                elif "EMPLOYMENT_LABOR" in primary_domains_for_cid and primary_domain == "CONFIDENTIALITY_NDA" and cid in ["POSITION_DUTIES", "COMPENSATION_BENEFITS", "EMPLOYMENT_TERM"]:
                    score -= 8.0
                    
                # 4. Positive Regex Pattern Matches (Capped to prevent keyword flooding)
                pat_matches = 0
                for pat in candidate.get("patterns", []):
                    matches = list(re.finditer(pat, lower_block, re.IGNORECASE))
                    if matches:
                        pat_matches += len(matches)
                        # Capture accurate evidence snippet
                        if not heading_matched or pat_matches == 1:
                            m_start = max(0, matches[0].start() - 20)
                            m_end = min(len(clean_text), matches[0].end() + 80)
                            best_evidence = clean_text[m_start:m_end].strip()

                # Cap pattern match bonus so body keywords don't override an explicit heading
                score += min(9.0, pat_matches * 3.0)
                
                # Penalty if general Confidentiality pattern tries to match a non-confidentiality heading
                if cid == "CONFIDENTIALITY_NDA" and not heading_matched and any(
                    k in lower_heading for k in ["termination", "term", "liability", "indemnity", "jurisdiction", "governing law", "dispute", "notices", "solicitation", "warranties"]
                ):
                    score -= 8.0
                        
                if score > best_score and score >= 2.5:
                    best_score = score
                    best_cid = cid
                    
            # Fallback if no specific pattern met threshold
            if not best_cid:
                heading_canonical = normalize_to_canonical_id(heading)
                if heading_canonical:
                    best_cid = heading_canonical
                else:
                    best_cid = "GENERAL_PROVISION"

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
                "evidence": best_evidence,
                "confidence": min(0.98, max(0.60, 0.60 + (best_score * 0.04)))
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
                    evidence=f"Heading: '{heading}' | Canonical: {best_cid} (Evidence: {best_evidence[:120]})",
                    claim=f"Identified {display_type} clause under {primary_domain} taxonomy.",
                    reason=f"Structured multi-factor classification matched canonical category '{best_cid}'.",
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
        """Segments raw text into structured clause units by numbered sections, decimal sub-sections, SCHEDULE/EXHIBIT/APPENDIX blocks, or paragraph headers."""
        blocks: List[Dict[str, Any]] = []
        
        # Regex to detect clause headings including decimal subsections, SCHEDULE, EXHIBIT, APPENDIX without consuming following newline
        pattern = r"(?:^|\n)\s*(?:Clause\s+\d+[\.\:]?|\d+(?:\.\d+)*\.?|\bSECTION\s+\d+(?:\.\d+)*[\.\:]?|\bARTICLE\s+[IVXLCDM\d]+[\.\:]?|\bSCHEDULE(?:\s+OF\s+PROPERTY|\s+[A-Z\d]+)?[\.\:]?|\bEXHIBIT\s+[A-Z\d]+[\.\:]?|\bAPPENDIX\s+[A-Z\d]+[\.\:]?)\s*([A-Za-z0-9\s&/,\-]{0,60}?)(?::|\.\s+|\Z|(?=\n))"
        
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        if len(matches) >= 2:
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                raw_heading = matches[i].group(0).strip().rstrip(":").rstrip(".")
                matched_sub = matches[i].group(1).strip()
                heading = matched_sub if matched_sub else raw_heading
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
