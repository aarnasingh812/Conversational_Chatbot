"""
rag.py — Core RAG pipeline for DocChat AI.
All LangChain / FAISS / Groq logic lives here; no UI framework dependency.
"""

import os
import time
import tempfile
from functools import lru_cache

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

from typing import List
from google import genai
from langchain_core.embeddings import Embeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain



class GeminiEmbeddings(Embeddings):

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> List[float]:
        result = self._client.models.embed_content(
            model=self._model,
            contents=text,
        )
        return result.embeddings[0].values


load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# SINGLETONS  (created once per process)
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Return a cached ChatGroq instance."""
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-120b",
    )


@lru_cache(maxsize=1)
def get_embeddings() -> GeminiEmbeddings:
    """Return Gemini embeddings via google-genai SDK (v1 API, no local ML libs)."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Get a free key at "
            "https://aistudio.google.com/apikey and add it to your .env file."
        )
    return GeminiEmbeddings(api_key=api_key, model="gemini-embedding-001")


# ─────────────────────────────────────────────────────────────────────────────
# RAG PROMPT
# ─────────────────────────────────────────────────────────────────────────────

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are a knowledgeable and helpful document assistant. Your job is to answer questions \
accurately based on the provided document context.

Guidelines:
- Answer clearly and concisely, using the context below.
- Use markdown formatting (bold, bullet lists, etc.) to improve readability when helpful.
- If the answer is NOT found in the context, say exactly:
  "I couldn't find that information in the uploaded document. Try rephrasing your question \
or ask about a topic covered in the document."
- Never fabricate information. Never go beyond what the context says.

<context>
{context}
</context>

User Question: {input}
""")


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def build_vector_store(pdf_bytes: bytes) -> tuple[FAISS, int, int]:
    """
    Persist PDF bytes to a temp file, load, chunk, embed, and return
    (FAISS vector store, page count, chunk count).
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        loader   = PyPDFLoader(tmp_path)
        docs     = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=200)
        chunks   = splitter.split_documents(docs)
        vectors  = FAISS.from_documents(chunks, get_embeddings())
        return vectors, len(docs), len(chunks)
    finally:
        os.unlink(tmp_path)


def answer_question(vectors: FAISS, query: str) -> dict:
    """
    Run the retrieval-augmented generation chain and return a dict with:
      - answer (str)
      - sources (list of dicts with page and excerpt)
      - elapsed (float, seconds)
    """
    llm             = get_llm()
    doc_chain       = create_stuff_documents_chain(llm, RAG_PROMPT)
    retriever       = vectors.as_retriever(search_kwargs={"k": 5})
    retrieval_chain = create_retrieval_chain(retriever, doc_chain)

    t0     = time.perf_counter()
    result = retrieval_chain.invoke({"input": query})
    elapsed = time.perf_counter() - t0

    raw_sources = result.get("context", [])
    sources = []
    for chunk in raw_sources:
        page_num = chunk.metadata.get("page", None)
        sources.append({
            "page":    (page_num + 1) if isinstance(page_num, int) else None,
            "excerpt": chunk.page_content[:400] + ("…" if len(chunk.page_content) > 400 else ""),
        })

    return {
        "answer":  result["answer"],
        "sources": sources,
        "elapsed": round(elapsed, 3),
    }
