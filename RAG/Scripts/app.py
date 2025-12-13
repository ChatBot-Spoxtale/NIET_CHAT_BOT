import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from Scripts.query_rag_bert import answer_question

app = FastAPI(
    title="BERT + FAISS RAG API",
    version="1.0"
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
        "question": req.question,
        "answer": answer
    }
