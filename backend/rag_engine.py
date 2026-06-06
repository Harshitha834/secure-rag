import os
import pickle
import textwrap
from typing import List, Tuple, Dict

import numpy as np
import requests

# ── Optional heavy imports (gracefully degrade for testing) ─────────────────
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:  
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

EMBED_MODEL = "all-MiniLM-L6-v2"
OLLAMA_URL  = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
INDEX_PATH  = "faiss_index.bin"
META_PATH   = "faiss_meta.pkl"
DIM         = 384          # all-MiniLM-L6-v2 output dimension
CHUNK_SIZE  = 400          # characters per chunk
CHUNK_OVERLAP = 80

# RBAC hierarchy: what a role can read
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "employee": ["employee"],
    "hr":       ["employee", "hr"],
    "admin":    ["employee", "hr", "admin"],
}


def _chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks."""
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]


class RAGEngine:
    def __init__(self):
        self._load_model()
        self._load_index()

    # ── Model ──────────────────────────────────────────────────────────────

    def _load_model(self):
        if ST_AVAILABLE:
            print(f"[RAG] Loading embedding model: {EMBED_MODEL}")
            self.model = SentenceTransformer(EMBED_MODEL)
        else:
            self.model = None
            print("[RAG] SentenceTransformers not available – using random embeddings (demo mode)")

    def _embed(self, texts: List[str]) -> np.ndarray:
        if self.model:
            return self.model.encode(texts, normalize_embeddings=True).astype("float32")
        # Demo fallback: deterministic random (reproducible per text)
        vecs = []
        for t in texts:
            rng = np.random.RandomState(abs(hash(t)) % (2**31))
            v = rng.randn(DIM).astype("float32")
            v /= np.linalg.norm(v) + 1e-9
            vecs.append(v)
        return np.array(vecs)

    # ── Index ──────────────────────────────────────────────────────────────

    def _load_index(self):
        if FAISS_AVAILABLE and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"[RAG] Loaded existing index with {self.index.ntotal} vectors")
        else:
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(DIM)   # Inner-product (cosine on normalised vecs)
            else:
                self.index = None
            self.metadata: List[Dict] = []
            print("[RAG] Created fresh index")

    def _save_index(self):
        if FAISS_AVAILABLE and self.index:
            faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    # ── Public API ─────────────────────────────────────────────────────────

    def add_document(self, text: str, filename: str, doc_role: str) -> int:
        chunks = _chunk_text(text)
        if not chunks:
            return 0
        vecs = self._embed(chunks)
        if FAISS_AVAILABLE and self.index:
            self.index.add(vecs)
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                "text":     chunk,
                "filename": filename,
                "role":     doc_role,
                "chunk_id": i,
            })
        self._save_index()
        return len(chunks)

    def list_documents(self, user_role: str) -> List[Dict]:
        allowed = ROLE_PERMISSIONS.get(user_role, [])
        seen, docs = set(), []
        for m in self.metadata:
            if m["role"] in allowed and m["filename"] not in seen:
                seen.add(m["filename"])
                docs.append({"filename": m["filename"], "role": m["role"]})
        return docs

    def query(self, query_text: str, user_role: str, top_k: int = 5) -> Tuple[str, List[str]]:
        allowed = ROLE_PERMISSIONS.get(user_role, [])

        if not self.metadata:
            return "No documents have been indexed yet. Please upload documents first.", []

        q_vec = self._embed([query_text])

        # Retrieve candidates
        if FAISS_AVAILABLE and self.index and self.index.ntotal > 0:
            k = min(top_k * 4, self.index.ntotal)
            _, indices = self.index.search(q_vec, k)
            candidates = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
        else:
            # Fallback: keyword search
            q_lower = query_text.lower()
            candidates = [m for m in self.metadata if any(w in m["text"].lower() for w in q_lower.split())]
            candidates = candidates[:top_k * 4]

        # RBAC filter
        filtered = [c for c in candidates if c["role"] in allowed]

        if not filtered:
            return (
                "I don't have access to documents relevant to your query, "
                "or the documents require higher permissions.",
                [],
            )

        context_chunks = filtered[:top_k]
        context = "\n\n---\n\n".join(c["text"] for c in context_chunks)
        sources = list({c["filename"] for c in context_chunks})

        answer = self._generate_answer(query_text, context)
        return answer, sources

    # ── LLM ───────────────────────────────────────────────────────────────

    def _generate_answer(self, question: str, context: str) -> str:
        prompt = (
            "You are a secure enterprise AI assistant. "
            "Answer ONLY based on the provided context. "
            "If the answer is not in the context, say 'I cannot find that information in the available documents.'\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except requests.exceptions.ConnectionError:
            return self._fallback_answer(question, context)
        except Exception as e:
            return f"LLM error: {e}"

    @staticmethod
    def _fallback_answer(question: str, context: str) -> str:
        """Simple keyword-based answer when Ollama is not running."""
        q_words = set(question.lower().split())
        best, best_score = "", 0
        for sentence in context.replace("\n", " ").split("."):
            score = sum(1 for w in q_words if w in sentence.lower())
            if score > best_score:
                best, best_score = sentence.strip(), score
        if best:
            return (
                f"[Ollama offline – keyword match] {best}.\n\n"
                "_Start Ollama (`ollama serve`) for full AI responses._"
            )
        return (
            "I found relevant documents but Ollama is not running. "
            "Please start Ollama with `ollama serve` and pull the model with `ollama pull phi3:mini`."
        )
