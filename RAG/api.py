from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Union

from constant.is_sensitive import is_sensitive_query
from constant.sensitive_redirect import SENSITIVE_REDIRECT_RESPONSE
from constant.is_sensitive import is_safety_confirmation_query
from constant.sensitive_redirect import POSITIVE_SENSITIVE_RESPONSE
from constant.llm_keywords import should_go_to_llm

from llm_model_gemini.chat import chat

from router.placement_router import router as placement_router
from router.callback_router import router as callback_router

from query_rag import answer_rag

app = FastAPI(title="NIET Course RAG Bot API")

app.include_router(callback_router, prefix="/api")
app.include_router(placement_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

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
def is_comparison_query(q: str) -> bool:
    q = q.lower()
    return any(kw in q for kw in [
        "better than",
        "vs",
        "versus",
        "instead of",
        "compare",
        "difference between",
        "which is better"
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

    question = payload.question.lower()

    try:
        # 1️⃣ Sensitive handling
        if is_sensitive_query(payload.question):
            if is_safety_confirmation_query(payload.question):
                return POSITIVE_SENSITIVE_RESPONSE
            return SENSITIVE_REDIRECT_RESPONSE

        # 2️⃣ Try RAG first (unless comparison)
        if not is_comparison_query(question):
            rag_answer = answer_rag(question)
            if rag_answer:
                return {
                    "type": "normal",
                    "answer": rag_answer
                }

        # 3️⃣ LLM keyword-based routing
        if should_go_to_llm(question):
            answer = chat(question)
            return {
                "type": "normal",
                "answer": answer
            }

        # 4️⃣ FINAL fallback → LLM (🚨 THIS WAS MISSING)
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
