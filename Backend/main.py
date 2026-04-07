from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import logging
from typing import Optional

from rag_processor import (
    load_documents,
    create_rag_index,
    load_vectorstore,
    query_rag,
    get_filtered_docs
)

from config import UPLOAD_FOLDER
from invoice_guardrails import extract_invoice_data

from user_db import users
from auth import create_token
from dependencies import get_current_user

# -------------------------
# App Initialization
# -------------------------
app = FastAPI(title="RBAC Enabled RAG Chatbot API")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = ["pdf", "txt"]

# -------------------------
# MODELS
# -------------------------
class QueryRequest(BaseModel):
    file_name: str
    question: str

class LoginRequest(BaseModel):
    username: str
    password: str

# -------------------------
# AUTH
# -------------------------
@app.post("/login")
def login(request: LoginRequest):
    user = users.get(request.username)

    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "username": request.username,
        "role": user["role"]
    })

    return {"access_token": token}

# -------------------------
# HELPERS
# -------------------------
def validate_file_extension(filename: str):
    ext = filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Only PDF and TXT allowed."
        )

def get_vectorstore_path(filename: str):
    return os.path.join("db", filename)

# -------------------------
# UPLOAD (RBAC)
# -------------------------
@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    print("USER:", user)
    try:
        validate_file_extension(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs("db", exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 🔥 Load docs WITH RBAC metadata
        documents = await asyncio.to_thread(
            load_documents,
            file_path,
            user["username"],
            user["role"]
        )

        persist_path = get_vectorstore_path(file.filename)

        await asyncio.to_thread(
            create_rag_index,
            documents,
            persist_path
        )

        return {
            "filename": file.filename,
            "uploaded_by": user["username"],
            "role": user["role"],
            "message": "File uploaded and indexed successfully."
        }

    except Exception as e:
        logger.exception(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed.")

# -------------------------
# QUERY (RBAC CORE)
# -------------------------
@app.post("/query/")
async def query(request: QueryRequest, user=Depends(get_current_user)):
    try:
        persist_path = get_vectorstore_path(request.file_name)

        if not os.path.exists(persist_path):
            raise HTTPException(status_code=404, detail="File not processed.")

        vectorstore = await asyncio.to_thread(
            load_vectorstore,
            persist_path
        )

        #  Apply RBAC filtering (CORRECT)
        filtered_docs = await asyncio.to_thread(
            get_filtered_docs,
            vectorstore,
            request.question,
            user
        )

        # Generate answer
        answer = await asyncio.to_thread(
            query_rag,
            filtered_docs,
            request.question
        )

        return {
            "user": user["username"],
            "role": user["role"],
            "question": request.question,
            "answer": answer
        }

    except Exception as e:
        logger.exception(f"Query error: {e}")
        raise HTTPException(status_code=500, detail="Query failed.")

# -------------------------
# INVOICE EXTRACTION (PROTECTED)
# -------------------------
@app.post("/extract_invoice/")
async def extract_invoice(file_name: str, question: Optional[str] = None, user=Depends(get_current_user)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found.")

        documents = await asyncio.to_thread(
            load_documents,
            file_path,
            user["username"],
            user["role"]
        )

        full_text = " ".join([doc.page_content for doc in documents])

        invoice_data = await asyncio.to_thread(
            extract_invoice_data,
            full_text,
            question
        )

        return {
            "user": user["username"],
            "data": invoice_data
        }

    except Exception as e:
        logger.exception(f"Invoice extraction error: {e}")
        raise HTTPException(status_code=500, detail="Invoice extraction failed.")







