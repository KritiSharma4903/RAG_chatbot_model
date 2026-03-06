import os
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_groq import ChatGroq

# Initialize Embeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  # change to "cuda" if GPU available
)

# Initialize LLM

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Load Documents

def load_documents(file_path: str):
    """Load TXT or PDF file and return documents"""

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
    return documents


# Create FAISS Index (Persistent)

def create_rag_index(documents, persist_path=None):
    vectorstore = FAISS.from_documents(documents, embeddings)
    if persist_path:
        vectorstore.save_local(persist_path)
    return vectorstore


# Load Existing Vector Store

def load_vectorstore(persist_path: str):
    """Load saved FAISS vector store"""

    if not os.path.exists(persist_path):
        raise ValueError("Vectorstore path does not exist.")

    return FAISS.load_local(persist_path, embeddings,allow_dangerous_deserialization=True)



# Query RAG (Retriever + LLM)

def query_rag(vector_store, query: str):
    """Retrieve context and generate answer"""

    # Retrieve top 3 similar docs
    retrieved_docs = vector_store.similarity_search(query, k=3)

    if not retrieved_docs:
        return "No relevant context found."

    context = "\n\n".join(
        doc.page_content for doc in retrieved_docs
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



# Debug Mode

if __name__ == "__main__":

    print("Running rag_processor in debug mode...")

    test_file = "test.txt"  # change this manually

    if not os.path.exists(test_file):
        print("Test file not found.")
        exit()

    docs = load_documents(test_file)

    persist_path = "test_db"

    vector_store = create_rag_index(docs, persist_path)

    vector_store = load_vectorstore(persist_path)

    question = "Explain the main idea of this document."

    answer = query_rag(vector_store, question)

    print("\nAnswer:\n", answer)
