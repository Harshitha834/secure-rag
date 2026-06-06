from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from auth import authenticate_user, create_access_token, get_current_user, USERS_DB
from rag_engine import RAGEngine
from security import detect_prompt_injection

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

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_role: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin/hr can upload documents")

    contents = await file.read()
    text = contents.decode("utf-8", errors="ignore")

    doc_count = rag.add_document(
        text=text,
        filename=file.filename,
        doc_role=doc_role,
    )
    return {"message": f"Document '{file.filename}' indexed successfully", "chunks": doc_count}

@app.get("/documents/list")
async def list_documents(current_user: dict = Depends(get_current_user)):
    docs = rag.list_documents(current_user["role"])
    return {"documents": docs, "role": current_user["role"]}

# ── Query ─────────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, current_user: dict = Depends(get_current_user)):
    # Prompt injection check
    injection = detect_prompt_injection(req.query)
    if injection:
        return QueryResponse(
            answer="⚠️ Request blocked for security reasons.",
            sources=[],
            security_alert=f"Prompt injection detected: {injection}",
        )

    answer, sources = rag.query(req.query, current_user["role"])
    return QueryResponse(answer=answer, sources=sources)

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
