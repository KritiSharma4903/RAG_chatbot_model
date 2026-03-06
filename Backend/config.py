import os
from dotenv import load_dotenv

load_dotenv()  

# API keys and model configs
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RAG_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # HuggingFace embedding model
RAG_LLM_MODEL = "llama-3.3-70b-versatile" 
UPLOAD_FOLDER = "Data/uploaded_files"
