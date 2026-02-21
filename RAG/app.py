from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Union
import re

from constant.is_sensitive import is_sensitive_query, is_safety_confirmation_query
from constant.sensitive_redirect import (
    SENSITIVE_REDIRECT_RESPONSE,
    POSITIVE_SENSITIVE_RESPONSE
)
from constant.llm_keywords import should_go_to_llm

from llm_model_gemini.chat import chat
from query_rag import answer_rag

from router.placement_router import router as placement_router
from router.callback_router import router as callback_router


# ---------------- APP ----------------

app = FastAPI(title="NIET Course RAG Bot API")

app.include_router(callback_router, prefix="/api")
app.include_router(placement_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- MODELS ----------------

class ChatRequest(BaseModel):
    question: str

class NormalChatResponse(BaseModel):
    type: str = "normal"
    answer: str

class Action(BaseModel):
    type: str
    label: str
    url: Optional[str] = None

class SensitiveRedirectResponse(BaseModel):
    type: str = "sensitive_redirect"
    text: str
    actions: List[Action]

class PositiveSensitiveResponse(BaseModel):
    type: str = "positive_sensitive"
    text: str
    details: List[str]
    actions: List[Action]


# ---------------- HELPERS ----------------

DECISION_PATTERNS = [
    "should i",
    "is it good",
    "is it safe",
    "worth it",
    "why should",
    "why choose",
    "can i",
    "will i",
]

def is_decision_query(q: str) -> bool:
    q = q.lower()
    return any(p in q for p in DECISION_PATTERNS)

def is_comparison_query(q: str) -> bool:
    q = q.lower()
    return any(kw in q for kw in [
        "which",
        "why",
        "better",
        "better than",
        "vs",
        "versus",
        "compare",
        "difference between"
    ])


def is_admission_decision_query(q: str) -> bool:
    q = q.lower().strip()
    return any(p in q for p in [
        "should i take admission",
        "should i join",
        "should i choose",
        "is it worth joining",
        "is it good to join",
        "join niet"
    ]) 
@app.post(
    "/chat",
    response_model=Union[
        NormalChatResponse,
        SensitiveRedirectResponse,
        PositiveSensitiveResponse
    ]
)
def chat_endpoint(payload: ChatRequest):

    question = payload.question.strip().lower()

    try:
        if is_sensitive_query(payload.question) and not is_admission_decision_query(payload.question):
            if is_safety_confirmation_query(payload.question):
                return POSITIVE_SENSITIVE_RESPONSE
            return SENSITIVE_REDIRECT_RESPONSE

        if is_admission_decision_query (payload.question):
            answer=chat(question)
            return {
                "type":"normal",
                "answer":answer
            }
        
        if is_decision_query(question):
            modified_prompt = (
        "Answer the following question in a helpful and encouraging tone "
        "for a student considering admission at NIET:\n\n"
        + question
    )

            answer = chat(modified_prompt)

            if not isinstance(answer, str) or not answer.strip():
                answer = (
            "Choosing NIET is a great decision as it offers strong academics, "
            "experienced faculty, and excellent placement support. "
            "For detailed guidance, you can contact our admission team."
        )

            return {
                "type": "normal",
                "answer": answer
    }


        if is_comparison_query(question):
            answer = chat(question)
            return {
                "type": "normal",
                "answer": answer
            }


        rag_answer = answer_rag(question)
        if isinstance(rag_answer, str) and rag_answer.strip():
            return {
                "type": "normal",
                "answer": rag_answer
            }


        answer = chat(question)
        return {
            "type": "normal",
            "answer": answer
        }

    except Exception as e:
        print("Chat error:", e)
        return {
            "type": "normal",
            "answer": (
                "Our system is currently experiencing high traffic. "
                "Please try again in a few minutes or visit our website: "
                "https://www.niet.co.in/"
            )
        }


@app.get("/")
def root():

    return {"status": "NIET MAIN CHATBOT RAG is running"}

