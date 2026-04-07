import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_groq import ChatGroq

# -------------------------------
# Initialize Embeddings
# -------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# -------------------------------
# Initialize LLM
# -------------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# -------------------------------
# Load Documents
# -------------------------------

def load_documents(file_path: str, username: str, user_role: str):
    """Load TXT or PDF file and attach RBAC metadata"""

    ext = file_path.split(".")[-1].lower()

    if ext == "txt":
        loader = TextLoader(file_path)

    elif ext == "pdf":
        loader = PyPDFLoader(file_path)

    else:
        raise ValueError("Unsupported file type. Only TXT and PDF allowed.")

    documents = loader.load()

    if not documents:
        raise ValueError("No content found in document.")

    # 🔥 Attach RBAC metadata
    for doc in documents:
        doc.metadata["owner"] = username
        doc.metadata["role"] = user_role

    return documents


# -------------------------------
# Create FAISS Index
# -------------------------------

def create_rag_index(documents, persist_path=None):
    vectorstore = FAISS.from_documents(documents, embeddings)

    if persist_path:
        vectorstore.save_local(persist_path)

    return vectorstore


# -------------------------------
# Load Vector Store
# -------------------------------

def load_vectorstore(persist_path: str):

    if not os.path.exists(persist_path):
        raise ValueError("Vectorstore path does not exist.")

    return FAISS.load_local(
        persist_path,
        embeddings,
        allow_dangerous_deserialization=True
    )


# -------------------------------
# 🔐 RBAC FILTER (IMPORTANT)
# -------------------------------

def get_filtered_docs(vector_store, query: str, user: dict):
    """
    Retrieve docs and apply RBAC filtering
    """

    # Step 1: Retrieve docs
    retrieved_docs = vector_store.similarity_search(query, k=5)

    # Step 2: Apply RBAC filter
    filtered_docs = [
        doc for doc in retrieved_docs
        if doc.metadata.get("owner") == user["username"]
        or doc.metadata.get("role") == user["role"]
    ]

    return filtered_docs


# -------------------------------
# Query RAG (UPDATED)
# -------------------------------

def query_rag(filtered_docs, query: str):
    """Generate answer using filtered docs"""

    if not filtered_docs:
        return "Access denied or no relevant data found."

    context = "\n\n".join(
        doc.page_content for doc in filtered_docs
    )

    prompt = f"""
You are a helpful AI assistant.
Answer the question only using the provided context.
If answer is not in context, say "Answer not found in document".

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content


# -------------------------------
# Debug Mode
# -------------------------------

if __name__ == "__main__":

    print("Running rag_processor in debug mode...")

    test_file = "test.txt"

    if not os.path.exists(test_file):
        print("Test file not found.")
        exit()

    # fake user
    user = {"username": "kriti", "role": "admin"}

    docs = load_documents(test_file, user["username"], user["role"])

    persist_path = "test_db"

    vector_store = create_rag_index(docs, persist_path)

    vector_store = load_vectorstore(persist_path)

    question = "Explain the main idea of this document."

    filtered_docs = get_filtered_docs(vector_store, question, user)

    answer = query_rag(filtered_docs, question)

    print("\nAnswer:\n", answer)