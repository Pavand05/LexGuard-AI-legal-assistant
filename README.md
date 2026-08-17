# LexGuard-MA: Multi-Agent Legal Document Intelligence & Contract Analysis Platform

**LexGuard-MA** is a research-grade, collaborative multi-agent legal intelligence platform built specifically for comprehensive contract analysis, risk scoring, DPDP Act 2023 compliance auditing, citation fact-checking, and interactive redlining.

---

## 🌟 Key Capabilities

- 🤖 **13 Specialized Legal Agents**: Document Intelligence, Clause Extraction (18+ categories), Multi-Dimensional Risk Assessment, DPDP Act Compliance, Contradiction Detection, Missing Clause Playbooks, Statutory Legal Research, Citation Verification, Contract Obligations Tracker, Negotiation Strategy, Visual Redlining Studio, Privacy & PII Protection, and Consensus Reviewer.
- ⚖️ **Indian Statutory Grounding**: Direct knowledge base and claim verification against the **Digital Personal Data Protection Act (DPDP Act 2023)**, **Indian Contract Act 1872** (e.g. Section 27 non-compete restraint), **Information Technology Act 2000** (Section 43A), and **Arbitration and Conciliation Act 1996**.
- 📐 **Contract Health Score**: Mathematical consensus formula (0–100) factoring severe liability risks, statutory non-compliance, missing clauses, and unverified citations with Human-in-the-loop (HITL) review triggers.
- 🔍 **Interactive Redlining Studio**: Visual tracked changes diff engine (`<ins>` and `<del>`) with acceptable fallback positions and instant Accept/Reject decision workflows.
- 🛡️ **Zero-Leakage Privacy Mode**: Masking of Indian Aadhaar numbers, PAN cards, bank account details, and sensitive PII before external LLM summarization.
- 📊 **AgentOps Observability & Live Benchmark Suite**: Real-time telemetry (agent latency ms, confidence scores, message traces) and empirical comparative evaluation comparing Single-Agent vs. Multi-Agent architectures.

---

## 🛠️ Architecture & Topologies

LexGuard-MA supports 4 execution topologies:
1. **Parallel Multi-Agent (Fastest / Recommended)**: Concurrent agent execution achieving sub-200ms latency.
2. **Sequential Multi-Agent**: Deep step-by-step contextual enrichment.
3. **Debate / Critic Review**: Citation and Reviewer agents challenge and adjudicate analytical findings.
4. **Single-Agent Baseline**: Monolithic baseline for research ablation.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Node.js 18+

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Open the Application
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000`

---

## 📚 Research Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md): Multi-agent orchestration, communication protocols, mathematical formulas, and data models.
- [AGENTS.md](AGENTS.md): Detailed specifications for all 13 specialized agents.
- [EVALUATION.md](EVALUATION.md): Experimental results, ablation study, and hallucination reduction benchmark.
- [SECURITY.md](SECURITY.md): DPDP Act 2023 compliance, data retention policy, and Privacy Mode architecture.

---

## 📄 License
This project is licensed under the MIT License.