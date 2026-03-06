from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import logging
from typing import Optional

from rag_processor import load_documents, create_rag_index, load_vectorstore, query_rag
from config import UPLOAD_FOLDER
from invoice_guardrails import extract_invoice_data

# App Initialization
app = FastAPI(title="Premium RAG Chatbot API")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORS (Change origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allowed file types
ALLOWED_EXTENSIONS = ["pdf", "txt"]

# Pydantic Models
class QueryRequest(BaseModel):
    file_name: str
    question: str

class InvoiceRequest(BaseModel):
    file_name: str
    question: Optional[str] = None

# Helper Functions
def validate_file_extension(filename: str):
    extension = filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        logger.error(f"Invalid file type attempted: {filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{extension}'. Only PDF and TXT files are allowed."
        )

def get_vectorstore_path(filename: str):
    return os.path.join("db", filename)

# Upload File API
@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file:
            logger.warning("No file received in upload request")
            raise HTTPException(status_code=400, detail="No file uploaded.")

        validate_file_extension(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs("db", exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File saved successfully: {file.filename}")

        # Load documents and create RAG index in separate thread
        documents = await asyncio.to_thread(load_documents, file_path)
        persist_path = get_vectorstore_path(file.filename)
        await asyncio.to_thread(create_rag_index, documents, persist_path)

        logger.info(f"Vector index created for {file.filename}")
        return {"filename": file.filename, "message": "File uploaded and indexed successfully."}

    except HTTPException as he:
        raise he
    except FileNotFoundError:
        logger.exception(f"Upload failed, file path not found: {file.filename}")
        raise HTTPException(status_code=404, detail="Upload failed: File path not found.")
    except PermissionError:
        logger.exception(f"Upload failed, permission denied for file: {file.filename}")
        raise HTTPException(status_code=403, detail="Upload failed: Permission denied.")
    except Exception as e:
        logger.exception(f"Unexpected error during file upload: {file.filename} | {e}")
        raise HTTPException(status_code=500, detail="Internal server error during file upload.")

# Query API
@app.post("/query/")
async def query(request: QueryRequest):
    try:
        persist_path = get_vectorstore_path(request.file_name)
        if not os.path.exists(persist_path):
            logger.warning(f"Query attempted on unprocessed file: {request.file_name}")
            raise HTTPException(status_code=404, detail="File not processed. Please upload first.")

        vectorstore = await asyncio.to_thread(load_vectorstore, persist_path)
        answer = await asyncio.to_thread(query_rag, vectorstore, request.question)

        logger.info(f"Query processed successfully for file {request.file_name}")
        return {"question": request.question, "answer": answer}

    except HTTPException as he:
        raise he
    except FileNotFoundError:
        logger.exception(f"Vectorstore file missing for: {request.file_name}")
        raise HTTPException(status_code=404, detail="Vectorstore not found for this file.")
    except PermissionError:
        logger.exception(f"Permission denied while accessing vectorstore: {request.file_name}")
        raise HTTPException(status_code=403, detail="Permission denied to access vectorstore.")
    except Exception as e:
        logger.exception(f"Unexpected error during query for file {request.file_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during query.")

# Invoice Extraction API
@app.post("/extract_invoice/")
async def extract_invoice(file_name: str, question: Optional[str] = None):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if not os.path.exists(file_path):
            logger.warning(f"Invoice extraction attempted on missing file: {file_name}")
            raise HTTPException(status_code=404, detail="File not found. Upload first.")

        # Load document
        documents = await asyncio.to_thread(load_documents, file_path)
        full_text = " ".join([doc.page_content for doc in documents])

        # Extract invoice data
        invoice_data = await asyncio.to_thread(extract_invoice_data, full_text, question=question)

        logger.info(f"Invoice extraction completed for file {file_name}")
        return invoice_data

    except HTTPException as he:
        raise he
    except FileNotFoundError:
        logger.exception(f"File not found during invoice extraction: {file_name}")
        raise HTTPException(status_code=404, detail="File missing during invoice extraction.")
    except PermissionError:
        logger.exception(f"Permission denied during invoice extraction: {file_name}")
        raise HTTPException(status_code=403, detail="Permission denied during invoice extraction.")
    except Exception as e:
        logger.exception(f"Unexpected error during invoice extraction: {file_name} | {e}")
        raise HTTPException(status_code=500, detail="Internal server error during invoice extraction.")
    


