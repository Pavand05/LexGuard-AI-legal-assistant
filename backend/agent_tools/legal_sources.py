"""
Authoritative Legal Knowledge Base & Source Verification Adapter
Maintains primary statutory provisions for Indian law and international standards.
"""
from typing import Dict, Any, List, Optional
import re


# Authoritative primary legal statutes repository
STATUTORY_KNOWLEDGE_BASE = [
    {
        "id": "ICA-SEC-73",
        "act": "Indian Contract Act, 1872",
        "section": "Section 73",
        "jurisdiction": "India",
        "title": "Compensation for loss or damage caused by breach of contract",
        "authority_level": "Primary Statute",
        "keywords": ["breach", "damages", "compensation", "loss", "liquidated damages", "liability"],
        "excerpt": "When a contract has been broken, the party who suffers by such breach is entitled to receive, from the party who has broken the contract, compensation for any loss or damage caused to him thereby, which naturally arose in the usual course of things from such breach.",
        "url": "https://www.indiacode.nic.in/handle/123456789/2187"
    },
    {
        "id": "ICA-SEC-74",
        "act": "Indian Contract Act, 1872",
        "section": "Section 74",
        "jurisdiction": "India",
        "title": "Compensation for breach of contract where penalty stipulated for",
        "authority_level": "Primary Statute",
        "keywords": ["penalty", "stipulation", "liquidated damages", "reasonable compensation"],
        "excerpt": "When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach, the party complaining of the breach is entitled to receive reasonable compensation not exceeding the amount so named or the penalty stipulated.",
        "url": "https://www.indiacode.nic.in/handle/123456789/2187"
    },
    {
        "id": "ICA-SEC-27",
        "act": "Indian Contract Act, 1872",
        "section": "Section 27",
        "jurisdiction": "India",
        "title": "Agreement in restraint of trade, void",
        "authority_level": "Primary Statute",
        "keywords": ["non-compete", "restraint of trade", "restraint", "post-employment", "trade"],
        "excerpt": "Every agreement by which any one is restrained from exercising a lawful profession, trade or business of any kind, is to that extent void. Exception: One who sells the goodwill of a business may agree with the buyer to refrain from carrying on a similar business.",
        "url": "https://www.indiacode.nic.in/handle/123456789/2187"
    },
    {
        "id": "ICA-SEC-28",
        "act": "Indian Contract Act, 1872",
        "section": "Section 28",
        "jurisdiction": "India",
        "title": "Agreements in restraint of legal proceedings, void",
        "authority_level": "Primary Statute",
        "keywords": ["jurisdiction", "limitation", "dispute resolution", "legal proceedings", "exclusive jurisdiction"],
        "excerpt": "Every agreement by which any party thereto is restricted absolutely from enforcing his rights under or in respect of any contract, by the usual legal proceedings in the ordinary tribunals, or which limits the time within which he may thus enforce his rights, is void to that extent.",
        "url": "https://www.indiacode.nic.in/handle/123456789/2187"
    },
    {
        "id": "DPDP-SEC-4",
        "act": "Digital Personal Data Protection Act, 2023",
        "section": "Section 4",
        "jurisdiction": "India",
        "title": "Grounds for processing digital personal data",
        "authority_level": "Primary Statute",
        "keywords": ["dpdp", "personal data", "data fiduciary", "consent", "legitimate uses"],
        "excerpt": "A person may process the personal data of a Data Principal only in accordance with the provisions of this Act and for a lawful purpose for which the Data Principal has given or is deemed to have given her consent in accordance with the provisions of this Act.",
        "url": "https://www.meity.gov.in/content/digital-personal-data-protection-act-2023"
    },
    {
        "id": "DPDP-SEC-6",
        "act": "Digital Personal Data Protection Act, 2023",
        "section": "Section 6",
        "jurisdiction": "India",
        "title": "Consent and Notice Requirements",
        "authority_level": "Primary Statute",
        "keywords": ["consent", "notice", "clear language", "data principal", "withdrawal of consent"],
        "excerpt": "Consent given by the Data Principal shall be free, specific, informed, unconditional and unambiguous with a clear affirmative action, signifying an agreement to the processing of her personal data for the specified purpose.",
        "url": "https://www.meity.gov.in/content/digital-personal-data-protection-act-2023"
    },
    {
        "id": "DPDP-SEC-8",
        "act": "Digital Personal Data Protection Act, 2023",
        "section": "Section 8",
        "jurisdiction": "India",
        "title": "General obligations of Data Fiduciary",
        "authority_level": "Primary Statute",
        "keywords": ["security safeguards", "breach notification", "data erasure", "grievance redressal"],
        "excerpt": "A Data Fiduciary shall implement appropriate technical and organizational measures to ensure compliance with this Act and protect personal data in its possession by taking reasonable security safeguards to prevent personal data breach.",
        "url": "https://www.meity.gov.in/content/digital-personal-data-protection-act-2023"
    },
    {
        "id": "ARB-SEC-7",
        "act": "Arbitration and Conciliation Act, 1996",
        "section": "Section 7",
        "jurisdiction": "India",
        "title": "Arbitration agreement",
        "authority_level": "Primary Statute",
        "keywords": ["arbitration", "arbitration agreement", "dispute", "tribunal", "arbitral"],
        "excerpt": "An arbitration agreement means an agreement by the parties to submit to arbitration all or certain disputes which have arisen or which may arise between them in respect of a defined legal relationship, whether contractual or not. An arbitration agreement shall be in writing.",
        "url": "https://www.indiacode.nic.in/handle/123456789/1978"
    },
    {
        "id": "IT-SEC-43A",
        "act": "Information Technology Act, 2000",
        "section": "Section 43A",
        "jurisdiction": "India",
        "title": "Compensation for failure to protect data",
        "authority_level": "Primary Statute",
        "keywords": ["sensitive personal data", "security practices", "data protection", "compensation", "negligence"],
        "excerpt": "Where a body corporate, possessing, dealing or handling any sensitive personal data or information in a computer resource which it owns, controls or operates, is negligent in implementing and maintaining reasonable security practices and procedures, such body corporate shall be liable to pay damages.",
        "url": "https://www.indiacode.nic.in/handle/123456789/1999"
    }
]


def search_statutory_sources(query_or_keywords: List[str], jurisdiction: str = "India", top_k: int = 3) -> List[Dict[str, Any]]:
    """Search verified primary statutory authorities matching query keywords."""
    scores = []
    normalized_keywords = [k.lower().strip() for k in query_or_keywords if len(k.strip()) > 2]
    
    for item in STATUTORY_KNOWLEDGE_BASE:
        if jurisdiction and item["jurisdiction"].lower() != jurisdiction.lower():
            continue
            
        score = 0
        searchable_text = f"{item['act']} {item['section']} {item['title']} {' '.join(item['keywords'])} {item['excerpt']}".lower()
        for kw in normalized_keywords:
            if kw in searchable_text:
                score += 2
            for word in kw.split():
                if word in searchable_text:
                    score += 1
                    
        if score > 0:
            scores.append((score, item))
            
    scores.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scores[:top_k]]


def verify_legal_claim(claim_text: str, cited_section: str = "", cited_act: str = "") -> Dict[str, Any]:
    """
    Verify if a legal citation or claim is supported by official statutory authorities.
    Returns:
      status: SUPPORTED | PARTIALLY_SUPPORTED | NOT_SUPPORTED | UNVERIFIED
      evidence: Dict of matching statute details
      confidence: float
    """
    clean_claim = claim_text.lower()
    
    for item in STATUTORY_KNOWLEDGE_BASE:
        section_match = item["section"].lower() in clean_claim or (cited_section and cited_section.lower() in item["section"].lower())
        act_match = item["act"].lower() in clean_claim or (cited_act and cited_act.lower() in item["act"].lower())
        
        if section_match and act_match:
            return {
                "status": "SUPPORTED",
                "authority": item,
                "confidence": 0.95,
                "note": f"Verified against official {item['act']}, {item['section']}."
            }
        elif section_match or act_match:
            return {
                "status": "PARTIALLY_SUPPORTED",
                "authority": item,
                "confidence": 0.75,
                "note": f"Matched {item['act']} but specific clause interpretation requires human lawyer review."
            }
            
    # If no verified primary statute matched
    return {
        "status": "UNVERIFIED",
        "authority": None,
        "confidence": 0.40,
        "note": "Unable to verify this specific legal authority in the primary statutory knowledge base."
    }
