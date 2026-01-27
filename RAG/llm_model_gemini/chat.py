# rag/chat.py

from llm_model_gemini.retriever.unified_retriever import retrieve_chunks
from llm_model_gemini.llm.gemini_client import generate_answer
from llm_model_gemini.memory.chat_memory import add, get
from llm_model_gemini.context_builder import build_context

def build_rag_context(chunks):
    texts = []

    for chunk in chunks:
        # case 1: chunk is dict
        if isinstance(chunk, dict):
            if "answer" in chunk:
                texts.append(chunk["answer"])
            elif "text" in chunk:
                texts.append(chunk["text"])

        # case 2: chunk is string
        elif isinstance(chunk, str):
            texts.append(chunk)

        # case 3: chunk is list
        elif isinstance(chunk, list):
            for item in chunk:
                if isinstance(item, str):
                    texts.append(item)

    return "\n".join(texts)

def chat(user_query: str):
    add("user", user_query)

    if "syllabus" in user_query.lower() or "pdf" in user_query.lower():
        reply = (
            "For the complete and official syllabus, please visit:\n\n"
            "https://www.niet.co.in/academics/syllabus"
        )
        add("assistant", reply)
        return reply

    data_context = build_context()

    chunks = retrieve_chunks(user_query, top_k=3)
    rag_context = build_rag_context(chunks) if chunks else ""

    final_context = data_context
    if rag_context:
        final_context += "\n\nADDITIONAL INFORMATION:\n" + rag_context

    reply = generate_answer(final_context, user_query, get())

    add("assistant", reply)
    return reply
