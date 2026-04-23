import services.tracing   
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
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
    query_rag
)

from config import UPLOAD_FOLDER
from invoice_guardrails import extract_invoice_data

from user_db import users
from auth import create_token
from dependencies import get_current_user

# ✅ FIXED IMPORT (IMPORTANT)
from services.llm_service import get_llm_response


# -------------------------
# APP INIT
# -------------------------
app = FastAPI(title="RBAC Enabled RAG Chatbot API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    question: str
    mode: str  # "general" | "rag"
    file_name: Optional[str] = None


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
            detail=f"Invalid file type: {ext}"
        )


def get_vectorstore_path(filename: str):
    return os.path.join("db", filename)


# -------------------------
# UPLOAD
# -------------------------
@app.post("/upload_file/")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        validate_file_extension(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs("db", exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

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
            "message": "Uploaded + Indexed successfully"
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Upload failed")


# -------------------------
# QUERY
# -------------------------
@app.post("/query/")
async def query(request: QueryRequest, user=Depends(get_current_user)):
    try:
        mode = request.mode.strip().lower()
        print("MODE RECEIVED:", request.mode)

        if mode == "general":
            answer = await asyncio.to_thread(
                get_llm_response,
                request.question
            )
            return {"mode": "general", "answer": answer}

        elif mode == "rag":
            if not request.file_name:
                raise HTTPException(status_code=400, detail="file_name required")

            file_path = get_vectorstore_path(request.file_name)

            answer = await asyncio.to_thread(
                query_rag,
                file_path,
                request.question,
                user
            )

            return {"mode": "rag", "answer": answer}

        else:
            raise HTTPException(status_code=400, detail="Invalid mode")

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Query failed")
    

# -------------------------
# INVOICE EXTRACTION
# -------------------------
@app.post("/extract_invoice/")
async def extract_invoice(
    file_name: str,
    question: Optional[str] = None,
    user=Depends(get_current_user)
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        documents = await asyncio.to_thread(
            load_documents,
            file_path,
            user["username"],
            user["role"]
        )

        full_text = " ".join([d.page_content for d in documents])

        invoice_data = await asyncio.to_thread(
            extract_invoice_data,
            full_text,
            question
        )

        return {
            "invoice_number": invoice_data.get("invoice_number"),
            "invoice_date": invoice_data.get("invoice_date"),
            "vendor_name": invoice_data.get("vendor_name"),
            "total_amount": invoice_data.get("total_amount"),
            "items": invoice_data.get("items", [])
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Invoice extraction failed")
    
    




