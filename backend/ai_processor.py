import re
import os
import sys
import math

# Load .env file if present (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass  # dotenv optional; user can also set env vars manually

# LangChain imports (langchain-core v1.x / langchain v1.x)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ─── LLM Loader ──────────────────────────────────────────────────────────────

def _load_llm():
    """
    Try to load a real LLM in priority order:
      1. Groq  (GROQ_API_KEY in env)
      2. MockLLM fallback
    Returns (llm, provider_name).
    """
    # ── 1. Groq ──────────────────────────────────────────────────────────────
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key and groq_key != "your_groq_api_key_here":
        try:
            from langchain_groq import ChatGroq
            model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
            llm = ChatGroq(api_key=groq_key, model_name=model, temperature=0.2)
            print(f"[LLM] Groq loaded — model: {model}")
            return llm, "groq"
        except Exception as e:
            print(f"[LLM] Groq init failed: {e}")

    # ── Fallback ──────────────────────────────────────────────────────────────
    print("[LLM] No API key found — using MockLLM fallback.")
    print("      Set GROQ_API_KEY in backend/.env to enable real AI answers.")
    return MockLLM(), "mock"


# ─── Legal Prompt ─────────────────────────────────────────────────────────────

LEGAL_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert legal assistant. Answer the user's question using ONLY "
     "the provided document context. Be precise, concise, and cite relevant "
     "clauses where possible. If the answer is not in the document, say so clearly."),
    ("human",
     "Document context:\n{context}\n\n"
     "Question: {question}"),
])

LEGAL_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert legal analyst. Summarize the following legal document in "
     "3-5 sentences. Identify the document type, key parties, main obligations, "
     "and any notable risk areas."),
    ("human", "{text}"),
])


# ─── Document Processor ───────────────────────────────────────────────────────

class DocumentProcessor:
    def __init__(self):
        self.llm = None
        self.provider = "mock"

    def initialize_llm(self, model_path=None):
        """Load the best available LLM."""
        self.llm, self.provider = _load_llm()

    # ── Text splitting ────────────────────────────────────────────────────────

    def split_text(self, text, chunk_size=1000, chunk_overlap=150):
        """Split text into overlapping chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)

    # ── Clause extraction ─────────────────────────────────────────────────────

    # Clause pattern definitions.
    # Rules applied to every pattern:
    #   • \b word-boundary anchors prevent matching inside longer words
    #     (e.g. "ip" must NOT fire on "equipment" or "subscription")
    #   • Each pattern captures up to the next blank line or CAPITALISED line
    CLAUSE_PATTERNS = [
        {
            "type": "Termination",
            # 'end' is too broad alone; require it as a whole word
            "pattern": r"\b(termination|terminate|terminates|cancellation|cancel)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "medium",
        },
        {
            "type": "Liability",
            "pattern": r"\b(liability|liable|indemnification|indemnify|indemnity|damages)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "high",
        },
        {
            "type": "Payment",
            # 'due' alone fires too often; require full words and exclude 'due to'
            "pattern": r"\b(payment|invoice|rent\s+shall\s+be|monthly\s+rent|security\s+deposit|shall\s+pay)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "low",
        },
        {
            "type": "Confidentiality",
            "pattern": r"\b(confidential|confidentiality|non-disclosure|proprietary\s+information|trade\s+secret)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "medium",
        },
        {
            "type": "Governing Law",
            "pattern": r"\b(governing\s+law|jurisdiction|applicable\s+law|choice\s+of\s+law|courts?\s+of)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "low",
        },
        {
            "type": "Non-Compete",
            "pattern": r"\b(non[- ]?compete|non[- ]?competition|restrictive\s+covenant|non[- ]?solicitation)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "high",
        },
        {
            "type": "Intellectual Property",
            # \bip\b matches only the standalone abbreviation, NOT inside other words
            "pattern": r"\b(intellectual\s+property|\bip\b|patent|copyright|trademark|trade\s+mark)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "medium",
        },
        {
            "type": "Force Majeure",
            "pattern": r"\b(force\s+majeure|act\s+of\s+god|natural\s+disaster|unforeseen\s+circumstances)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "medium",
        },
        {
            "type": "Dispute Resolution",
            "pattern": r"\b(arbitration|mediation|dispute\s+resolution|dispute\s+settlement|settle\s+disputes?)\b[^\n]*(?:\n(?!\n)[^\n]*)*",
            "risk": "medium",
        },
    ]

    def extract_clauses(self, text, page_texts=None):
        """
        Extract legal clauses using curated regex patterns.

        Args:
            text:        Full document text.
            page_texts:  Optional list of per-page strings; enables real page numbers.
        Returns:
            List of clause dicts.
        """
        MIN_CONTENT_LEN = 60   # skip trivially short matches
        MAX_CONTENT_LEN = 400  # truncate very long snippets

        # Build a page-offset map so we can report real page numbers
        page_offsets = []  # list of (start_char, page_number)
        if page_texts:
            offset = 0
            for page_num, pg_text in enumerate(page_texts, start=1):
                page_offsets.append((offset, page_num))
                offset += len(pg_text)

        def char_to_page(pos):
            """Return 1-based page number for a character position."""
            if not page_offsets:
                return 1
            page = 1
            for (start, pg) in page_offsets:
                if pos >= start:
                    page = pg
                else:
                    break
            return page

        clauses = []
        seen_fingerprints = set()  # deduplication

        for pi in self.CLAUSE_PATTERNS:
            for match in re.finditer(pi["pattern"], text, re.IGNORECASE):
                content = match.group(0).strip()

                # ── 1. Minimum length filter ───────────────────────────────
                if len(content) < MIN_CONTENT_LEN:
                    continue

                # ── 2. Deduplication by fingerprint (first 80 chars, normalised) ─
                fingerprint = re.sub(r"\s+", " ", content[:80].lower())
                if fingerprint in seen_fingerprints:
                    continue
                seen_fingerprints.add(fingerprint)

                # ── 3. Page number ─────────────────────────────────────────
                page_num = char_to_page(match.start())

                # ── 4. Human-readable description ──────────────────────────
                snippet = content[:120].replace("\n", " ").strip()
                description = f'{pi["type"]} clause: "{snippet}..."'

                clauses.append({
                    "type":        pi["type"],
                    "description": description,
                    "risk":        pi["risk"],
                    "content":     content[:MAX_CONTENT_LEN] + "..." if len(content) > MAX_CONTENT_LEN else content,
                    "page":        page_num,
                })
        return clauses

    # ── Summarisation ─────────────────────────────────────────────────────────

    def summarize_document(self, text):
        """Generate a document summary — AI-powered when an LLM is available."""
        # Try real LLM first
        if self.llm and not isinstance(self.llm, MockLLM):
            try:
                chain = LEGAL_SUMMARY_PROMPT | self.llm | StrOutputParser()
                # Send first 6000 chars to stay within token limits
                return chain.invoke({"text": text[:6000]})
            except Exception as e:
                print(f"[summarize] LLM call failed, falling back to regex: {e}")

        # Regex-based fallback
        doc_type = "legal document"
        lower = text.lower()
        if any(w in lower for w in ["agreement", "contract"]):
            doc_type = "legal agreement or contract"
        elif "employment" in lower:
            doc_type = "employment agreement"
        elif "lease" in lower:
            doc_type = "lease agreement"

        key_terms = {k: lower.count(k) for k in
                     ["payment", "termination", "liability", "confidentiality", "breach", "damages"]}
        word_count = len(text.split())
        high_risk = sum(1 for t in ["liability", "breach", "damages"] if key_terms[t] > 0)

        parts = [
            f"This appears to be a {doc_type}.",
            f"Document contains {key_terms['payment']} payment-related terms, "
            f"{key_terms['termination']} termination clauses, "
            f"{key_terms['liability']} liability provisions, "
            f"{key_terms['confidentiality']} confidentiality terms, "
            f"{key_terms['breach']} breach clauses, and "
            f"{key_terms['damages']} damages provisions.",
            f"Document is approximately {word_count} words long.",
        ]
        if high_risk:
            parts.append(f"Document contains {high_risk} high-risk elements that require careful review.")
        return " ".join(parts)

    # ── Risk analysis ─────────────────────────────────────────────────────────

    def analyze_risks(self, clauses):
        """Tally risk levels from extracted clauses."""
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for clause in clauses:
            risk = clause.get("risk", "low")
            if risk in risk_counts:
                risk_counts[risk] += 1
        risk_counts["total"] = len(clauses)
        return risk_counts

    # ── RAG Q&A ───────────────────────────────────────────────────────────────

    def _keyword_retrieve(self, question, chunks, k=4):
        """
        Fast keyword-based retrieval — no model download needed.
        Scores each chunk by how many question words it contains, then
        returns the top-k chunks.
        """
        q_words = set(re.sub(r"[^\w\s]", "", question.lower()).split())
        # Remove very common stop words
        stop = {"is", "are", "the", "a", "an", "there", "in", "of", "to",
                "and", "or", "for", "with", "any", "what", "does", "do",
                "how", "when", "where", "which", "who", "it", "this", "that"}
        q_words -= stop

        scored = []
        for chunk in chunks:
            lower = chunk.lower()
            score = sum(1 for w in q_words if w in lower)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:k]]

    def rag_qa(self, question, document_text, use_chroma=False):
        """
        Q&A over the document.
        - When a real LLM (Groq) is available: uses fast keyword retrieval to
          find the most relevant chunks, then sends them to Groq.  No local
          embedding model download required.
        - When only MockLLM is available: falls back to the same keyword
          retrieval and returns the raw excerpts.
        - When use_chroma=True *and* no real LLM: uses FAISS with the cached
          HuggingFace embeddings model (loaded once globally).
        """
        global _embeddings_cache

        llm = self.llm if self.llm else MockLLM()
        texts = self.split_text(document_text)

        if not isinstance(llm, MockLLM):
            # ── Fast path: keyword retrieval + Groq ──────────────────────────
            best_chunks = self._keyword_retrieve(question, texts, k=5)
            context = "\n\n".join(best_chunks)
            chain   = LEGAL_QA_PROMPT | llm | StrOutputParser()
            answer  = chain.invoke({"context": context, "question": question})
            return {"answer": answer, "sources": best_chunks}

        # ── Slow path: load/reuse cached HuggingFace embeddings ──────────────
        if _embeddings_cache is None:
            print("[RAG] Loading HuggingFace embeddings model (first time only)...")
            _embeddings_cache = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            print("[RAG] Embeddings model loaded and cached.")

        docs      = [Document(page_content=chunk) for chunk in texts]
        vectordb  = FAISS.from_documents(docs, _embeddings_cache)
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})

        source_docs = retriever.invoke(question)
        context     = "\n\n".join(doc.page_content for doc in source_docs)
        answer      = llm(context, question)
        return {"answer": answer, "sources": [d.page_content for d in source_docs]}


# ─── Mock LLM (fallback only) ─────────────────────────────────────────────────

class MockLLM:
    """Returns relevant document snippets when no real LLM is configured."""
    def __call__(self, context, question=""):
        if context:
            return (
                "**[AI Fallback Mode]** No LLM API key is configured.\n\n"
                "Most relevant document excerpt:\n\n"
                f"{context[:800]}\n\n"
                "_To get real AI answers: add your free Groq API key to `backend/.env`._"
            )
        return "No relevant content found in the document for your question."


# ─── Global instances ─────────────────────────────────────────────────────────

_embeddings_cache = None          # HuggingFaceEmbeddings loaded once on first use
document_processor = DocumentProcessor()