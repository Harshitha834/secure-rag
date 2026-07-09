from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from document_processor import DocumentProcessor
from audit_logger import AuditLogger
from file_extractor import (extract_text, is_supported, SUPPORTED_EXTENSIONS,)

from auth import authenticate_user, create_access_token, get_current_user, register_user
from rag_engine import RAGEngine
from security import detect_prompt_injection
from rate_limiter import RateLimiter, UploadRateLimiter

app = FastAPI(title="Secure RAG Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()

# ── Models ──────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    security_alert: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

# ── Auth ─────────────────────────────────────────────────────────────────────
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

@app.post("/auth/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    user = register_user(
        data.username,
        data.password,
        data.role
    )

    token = create_access_token({
        "sub": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
    }

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}

# ── Documents ─────────────────────────────────────────────────────────────────
@app.get("/documents/supported-formats")
async def supported_formats():
    return {"extensions": sorted(SUPPORTED_EXTENSIONS)}
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_role: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin/hr can upload documents")

    if not UploadRateLimiter.is_allowed(current_user["username"]):
        raise HTTPException(status_code=429, detail="Upload rate limit exceeded.")

    if not is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    contents = await file.read()

    max_size = 25 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {max_size/(1024*1024)} MB limit",
        )

    text, warning = extract_text(file.filename, contents)

    if not text.strip():
        raise HTTPException(status_code=422, detail="Extracted text is empty")

    doc_count = rag.add_document(
        text=text,
        filename=file.filename,
        doc_role=doc_role,
    )

    # Audit log AFTER doc_count exists
    AuditLogger.log_event(
        event_type="DOCUMENT_UPLOAD",
        username=current_user["username"],
        role=current_user["role"],
        details={
            "filename": file.filename,
            "document_role": doc_role,
            "chunks": doc_count,
        },
    )

    response = {
        "message": f"Document '{file.filename}' uploaded successfully with {doc_count} chunks.",
        "chunks": doc_count,
    }
    if warning:
        response["warning"] = warning

    return response

@app.get("/documents/list")
async def list_documents(current_user: dict = Depends(get_current_user)):
    docs = rag.list_documents(current_user["role"])
    return {"documents": docs, "role": current_user["role"]}

# ── Query ─────────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, current_user: dict = Depends(get_current_user)):

    if not RateLimiter.is_allowed(current_user["username"]):
        raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded. Please try again later."
    )
    # Prompt injection check
    injection = detect_prompt_injection(req.query)
    if injection:
        AuditLogger.log_event(
        event_type="PROMPT_INJECTION",
        username=current_user["username"],
        role=current_user["role"],
        details={
            "query": req.query,
            "reason": injection,
        }
    )
        return QueryResponse(
            answer="⚠️ Request blocked for security reasons.",
            sources=[],
            security_alert=f"Prompt injection detected: {injection}",
        )

    answer, sources = rag.query(req.query, current_user["role"])
    AuditLogger.log_event(
    event_type="QUERY",
    username=current_user["username"],
    role=current_user["role"],
    details={
        "query": req.query,
        "sources": sources,
    }
)
    return QueryResponse(answer=answer, sources=sources)

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
