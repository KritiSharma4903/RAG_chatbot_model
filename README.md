# 🤖 RAG Chatbot Model

A Retrieval-Augmented Generation (RAG) based chatbot that answers user queries using context from custom documents. This project combines LLMs, embeddings, and vector search to provide accurate, context-aware responses.

---

## 🚀 Features

- 🔍 Semantic search using embeddings
- 🧠 Context-aware responses using RAG pipeline
- 📂 Supports multiple document inputs
- ⚡ Fast inference using Groq / LLM APIs
- 🧩 Modular architecture (easy to extend)

---

## 🏗️ Tech Stack

- **Language:** Python
- **LLM:** Groq (Mixtral / LLaMA models)
- **Embeddings:** Local embedding model (nomic / others)
- **Vector DB:** Chroma / FAISS
- **Framework:** LangChain
- **UI (optional):** Gradio / Streamlit

---

RAG_chatbot_model/
│── app.py / main.py # Entry point
│── config.yaml # Configuration file
│── data/ # Input documents
│── embeddings/ # Embedding logic
│── vector_store/ # Vector database
│── utils/ # Helper functions
│── requirements.txt # Dependencies


🔑 Environment Variables
Create a .env file and add:
GROQ_API_KEY=your_api_key_here


🧠 How It Works
Documents are loaded and split into chunks
Each chunk is converted into embeddings
Embeddings are stored in a vector database
User query is converted into embedding
Relevant chunks are retrieved
LLM generates answer using retrieved context


