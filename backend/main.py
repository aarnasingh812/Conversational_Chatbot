
import uuid
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import build_vector_store, answer_question
from langchain_community.vectorstores import FAISS

# ─────────────────────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="DocChat AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store:  session_id -> {vectors, doc_name, pages, chunks}
sessions: Dict[str, dict] = {}


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    question:   str


class ChatResponse(BaseModel):
    answer:    str
    sources:   list
    elapsed:   float
    session_id: str


class UploadResponse(BaseModel):
    session_id: str
    doc_name:   str
    pages:      int
    chunks:     int


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Accept a PDF, build a FAISS vector store, return a session_id."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()

    try:
        vectors, pages, chunks = build_vector_store(pdf_bytes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "vectors":  vectors,
        "doc_name": file.filename,
        "pages":    pages,
        "chunks":   chunks,
    }

    return UploadResponse(
        session_id=session_id,
        doc_name=file.filename,
        pages=pages,
        chunks=chunks,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Run the RAG pipeline for a given session and question."""
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Please re-upload the document.")

    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_question(session["vectors"], req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG error: {exc}")

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        elapsed=result["elapsed"],
        session_id=req.session_id,
    )


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Remove a session and free its FAISS store from memory."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del sessions[session_id]
    return {"detail": "Session deleted."}
