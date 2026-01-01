import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[0]
sys.path.append(str(ROOT))

from RAG.query_rag_2 import answer_rag
from Ollama.llm_client import ask_ollama_with_context


app = FastAPI(
    title="NIET Chat API",
    version="3.1 - Greeting Only LLM"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://niet-chat-bot.onrender.com",       
        "https://niet-chat-bot-rag.onrender.com",   
        "http://localhost:3000",                    
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],       
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin"],
)

class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "Server Running ✔", "version": "3.1"}

GREETINGS = [
        "hi", "hello", "hey",
        "good morning", "good afternoon",
        "good evening", "namaste"
    ]
SMALL_TALK = [
        "how are you","how r u","how's you","how are u",
        "what's up","sup","how is your day",
        "kya haal hai","kaisa ho","kaise ho","sab theek"
    ]

COURSE_INDICATORS = [
    "btech","b.tech","mtech","m.tech","mba","mca","bca","bba",
    "cse","it","aiml","ai ml","ece","civil","mechanical",
    "syllabus","seats","duration","fees","eligibility","placement"
]



@app.post("/chat")
def chat(req: QueryRequest):
    user_query = req.question.strip()
    lowered = user_query.lower()

    if lowered in GREETINGS:
        return {"source":"llm-greeting","answer": ask_ollama_with_context(lowered)}

    if any(g in lowered for g in SMALL_TALK):
        return {
            "source": "llm-smalltalk",
            "answer": "I'm doing great! 😄 How are you? How can I help you today?"
        }
    if not any(word in lowered for word in COURSE_INDICATORS):
        return {
        "source": "chat-mode",
        "answer": "Thank you! 😄 I'm here to help. Tell me which course or topic you want information about!"
    }
    for g in GREETINGS:
        if lowered.startswith(g + " "):
            return {"source":"llm-greeting-question","answer": ask_ollama_with_context(lowered)}

    rag_answer = answer_rag(lowered)
    if rag_answer:
        return {"source":"rag","answer": rag_answer}

    return {"source":"none","answer":"I don't have data for this. Please re-check your question."}
