import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from Scripts.query_rag_bert import answer_question

app = FastAPI(
    title="BERT + FAISS RAG API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://niet-chat-bot.onrender.com/",
    "https://niet-chat-bot-rag.onrender.com"
],          
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],          
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def health():
    return {"status": "RAG server running"}

@app.post("/chat")
def chat(req: QueryRequest):
    answer = answer_question(req.question)
    return {
        "answer": answer,
    }

