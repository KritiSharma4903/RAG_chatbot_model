import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "RAG-CHATBOT-MODEL"

# -------------------------------
# API KEY CHECK (IMPORTANT)
# -------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")

# -------------------------------
# Embeddings
# -------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# -------------------------------
# LLM (FIXED)
# -------------------------------
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

# -------------------------------
# Load Documents
# -------------------------------
def load_documents(file_path: str, username: str, user_role: str):

    ext = file_path.split(".")[-1].lower()

    if ext == "txt":
        loader = TextLoader(file_path)
    elif ext == "pdf":
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError("Only TXT and PDF allowed")

    documents = loader.load()

    for doc in documents:
        doc.metadata["owner"] = username
        doc.metadata["role"] = user_role

    return documents


# -------------------------------
# Create FAISS
# -------------------------------
def create_rag_index(documents, persist_path):
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(persist_path)
    return vectorstore


# -------------------------------
# Load FAISS
# -------------------------------
import os

def load_vectorstore(persist_path):
    if not os.path.exists(persist_path):
        raise ValueError("Vector DB not found. Please create index first.")

    return FAISS.load_local(
        persist_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

# -------------------------------
# RBAC FILTER
# -------------------------------
def get_filtered_docs(vector_store, query: str, user: dict):

    retrieved_docs = vector_store.similarity_search(query, k=5)

    return [
        doc for doc in retrieved_docs
        if doc.metadata.get("owner") == user["username"]
        or doc.metadata.get("role") == user["role"]
    ]


# -------------------------------
# RAG QUERY (FIXED)
# -------------------------------
def query_rag(file_path: str, query: str, user: dict):

    vector_store = load_vectorstore(file_path)
    docs = get_filtered_docs(vector_store, query, user)

    if not docs:
        return llm.invoke(query).content

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_template("""
Answer ONLY using the context below.
If answer is not present, say "Not in document".

Context:
{context}

Question:
{question}
""")

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": query
    })

    return response.content


