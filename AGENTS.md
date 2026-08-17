# LexGuard-MA: Specialized Legal Agents Specification

LexGuard-MA utilizes a federation of 13 purpose-built intelligent agents. Each agent specializes in a distinct legal sub-discipline:

| # | Agent Name | Domain / Capability | Statutory Framework |
|---|---|---|---|
| 1 | **Document Intelligence Agent** | Document classification, entity extraction, party roles, and jurisdiction discovery | Private International Law, Stamp Act |
| 2 | **Clause Intelligence Agent** | 18+ clause category boundary identification, semantic extraction | Standard Commercial Contracting |
| 3 | **Risk Assessment Agent** | 6-dimensional risk matrix calculation (Legal, Financial, Compliance, Privacy, Operational, IP) | Contract Law & Tort Liability |
| 4 | **Compliance & DPDP Agent** | Cross-statutory compliance verification, non-compete restraint check, arbitration enforceability | DPDP Act 2023, Section 27 Contract Act, IT Act |
| 5 | **Contradiction Detection Agent** | Cross-clause contradiction, numerical & temporal deadline mismatch detection | Evidentiary & Drafting Rules |
| 6 | **Missing Clause Agent** | Standard contract completeness playbooks, gap analysis | Commercial Playbooks (NDA, SaaS, Employment, Lease) |
| 7 | **Legal Research Agent** | Statutory indexing, relevant sections & legal precedents retrieval | India Code & Central Acts |
| 8 | **Citation Verification Agent** | Claim grounding, anti-hallucination verification against primary statutory texts | Factual Grounding Engine |
| 9 | **Obligation Extraction Agent** | Party-wise affirmative/negative duty extraction with deadlines & default penalties | Contract Administration |
| 10 | **Negotiation Strategy Agent** | Balanced clause recommendations, fallback positions, concession strategy | Commercial Negotiation Playbooks |
| 11 | **Redlining Intelligence Agent** | Visual diff markup generation (`<ins>` and `<del>`), tracked changes studio | Legal Drafting Standards |
| 12 | **Privacy & PII Agent** | Sensitive personal data detection (Aadhaar, PAN, Bank Accounts, PII) and zero-leakage masking | DPDP Act 2023 & Section 43A IT Act |
| 13 | **Reviewer & Critic Agent** | Cross-agent consensus validation, health scoring, Human-in-the-loop review triggering | Quality Assurance & Adjudication |

---

## Agent Output Contracts

Every agent implements `BaseAgent.execute(context)` returning an `AgentResult` object containing:
- `agent_name`: Name identifier
- `status`: Execution state (`success` / `failed`)
- `confidence`: Calibrated confidence coefficient (0.0 to 1.0)
- `duration_ms`: Wall-clock execution time
- `findings`: List of `AgentFindingModel` instances
- `data`: Specialized dictionary payload (e.g. redline diffs, extracted obligations, extracted parties)
