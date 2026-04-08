# Chatbot Backend (FastAPI + LangChain + LangGraph + PostgreSQL)

An AI-powered chatbot backend built using FastAPI, LangChain, and LangGraph with support for RAG (Retrieval-Augmented Generation), web search, and Gmail integration.

---

## Features

- User Authentication (JWT-based login)
- Upload and process documents (PDF, DOCX)
- RAG-based question answering over uploaded documents
- Web search using Tavily API
- Gmail integration (fetch and analyze emails)
- Multi-tool orchestration using LangGraph
- PostgreSQL with pgvector for embedding storage

---

## Tech Stack

- Backend: FastAPI
- LLM Framework: LangChain, LangGraph
- Database: PostgreSQL (pgvector)
- Embeddings: Gemini Embeddings API
- Search: Tavily API
- Authentication: JWT

---

## API Endpoints

### Auth
- `POST /register` -> Register user
- `POST /login` → Login user

### Upload
- `POST /upload` → Upload PDF/DOCX files

### Chat
- `POST /ask` → Ask questions (RAG + tools)

---

## RAG Pipeline

1. Upload document
2. Extract text
3. Chunk text using RecursiveCharacterTextSplitter
4. Generate embeddings (Gemini)
5. Store embeddings in PostgreSQL (pgvector)
6. Retrieve relevant chunks during queries

---

##  Environment Variables

Create a `.env` file in the root directory:


JWT_SECRET=your_jwt_scret_key

Database

DATABASE_URL=postgresql://username:password@localhost:5432/db_name

Gemini API

GEMINI_API_KEY=your_gemini_api_key

Tavily API

TAVILY_API_KEY=your_tavily_api_key

Gmail

EMAIL_PASS=Your_app_password

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT = 587

EMAIL_USER=your_email_id

---

## Installation

```bash
git clone https://github.com/sunabh07/Chatbot-Backend
cd chatbot-backend

python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```
---

## Run The Server

uvicorn app.main:app --reload

---

## Contribution

Contributions are welcome! Feel free to fork and submit a PR.
