from llm_client import call_ollama

SYSTEM_PROMPT = (
    "You are a friendly and helpful assistant. "
    "Answer naturally. Be playful for creative questions."
)

def general_answer(user_query: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_query}\nAssistant:"
    return call_ollama(prompt)

print(general_answer(SYSTEM_PROMPT))