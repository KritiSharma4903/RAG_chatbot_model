# 🤖 RAG Chatbot Model

A Retrieval-Augmented Generation (RAG) chatbot built using Python, FastAPI, LangChain, vector search, and Groq LLMs.

This project answers user questions by retrieving relevant information from uploaded documents and passing that context to a Large Language Model for grounded, context-aware responses.

Instead of relying only on the LLM’s internal knowledge, the system performs retrieval first, then generation.

---

## 🚀 Features

- Semantic document retrieval using embeddings  
- Retrieval-Augmented Generation (RAG) pipeline  
- Context-aware response generation  
- Modular backend architecture with service layer  
- Vector database integration  
- Groq-powered fast LLM inference  
- Frontend for user interaction  
- Docker support for deployment  
- Extensible project structure for future upgrades

---

## 🏗️ Tech Stack

### Language
- Python

### Frameworks
- FastAPI  
- LangChain

### LLM
- Groq API  
- Mixtral / LLaMA Models

### Embeddings
- Nomic Embeddings (or local embedding models)

### Vector Database
- ChromaDB / FAISS

### Frontend
- Streamlit

### Deployment
- Docker

---

# 🧠 How RAG Works in This Project

The pipeline follows these steps:

1. Documents are loaded  
2. Documents are split into chunks  
3. Chunks are converted into embeddings  
4. Embeddings are stored in a vector database  
5. User enters a query  
6. Query is embedded  
7. Relevant chunks are retrieved  
8. Retrieved context is sent to the LLM  
9. LLM generates grounded response

Flow:

```text
User Query
   ↓
Query Embedding
   ↓
Vector Search
   ↓
Relevant Context Retrieval
   ↓
LLM (Groq)
   ↓
Final Response
```

---

# 📂 Project Structure

```text
RAG_chatbot_model/
│
├── Backend/
│   ├── main.py
│   ├── rag_processor.py
│   ├── services/
│   └── ...
│
├── Frontend/
│   ├── app.py
│
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/KritiSharma4903/RAG_chatbot_model.git

cd RAG_chatbot_model
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_api_key_here
```

---

# ▶️ Run the Project

Backend:

```bash
cd Backend

python main.py
```

or

```bash
uvicorn main:app --reload
```

Frontend:

```bash
cd Frontend

streamlit run app.py
```

---

# 🐳 Run With Docker

Build:

```bash
docker build -t rag-chatbot .
```

Run:

```bash
docker run -p 8000:8000 rag-chatbot
```

---

# 📌 Example Use Cases

- PDF Question Answering  
- Knowledge Base Assistant  
- Internal Company Chatbot  
- Research Document Assistant  
- Domain-specific RAG Assistant

---

# 🔮 Future Improvements

- Chat history memory  
- Hybrid Search (BM25 + Vector Search)  
- Reranking layer  
- Multi-document upload support  
- Evaluation pipeline (RAGAS)  
- Authentication and production deployment

---

# 📈 Architecture Concepts Used

This project demonstrates:

- Embeddings  
- Vector Databases  
- Retrieval Pipelines  
- Prompt Augmentation  
- Context Grounding  
- Modular Service Architecture

---

# 👩‍💻 Author

Kriti Sharma

GitHub:
https://github.com/KritiSharma4903

---

# ⭐ If you find this useful, consider starring the repository.