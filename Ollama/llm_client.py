import os
import requests

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "https://carman-unexercisable-snarly.ngrok-free.dev/api/generate"
)
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma3:1b")


def ask_ollama_with_context(user_query: str, rag_context: str = "") -> str:
    query = user_query.lower().strip()

    GREETINGS = ["hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"]
    GENERAL = ["how are you", "what's up", "how is your day", "kaisa ho", "kya haal hai"]

    if query in GREETINGS:
        return f"{user_query.capitalize()}! 👋 How can I assist you today?"

    if any(g in query for g in GENERAL):
        return "I'm doing well and happy to help! 😊 What would you like to know about NIET?"

    return ask_ollama_raw(user_query)


def ask_ollama_raw(prompt: str) -> str:
    HUMANIZED_PROMPT = f"""
You are NIET’s Virtual Assistant with friendly personality.

🎯 YOUR ROLES:
- Respond to greetings & small conversation
- Answer general questions like "how are you"
- If user asks NIET query, respond with helpful info
- If unclear, ask politely for clarification

🤝 GREETING & SMALL TALK STYLE:
- Warm and friendly tone
- Short, human-like, 2-3 lines max
- Emoji allowed but not spammed
Example:
"Hey! I'm doing great 😊 How can I help you today?"

🏫 NIET QUERY MODE:
- Be specific, informative, and clean
- If the question is incomplete, ask for missing detail

==================
USER QUESTION:
{prompt}
==================
"""
    payload = {
        "model": MODEL_NAME,
        "prompt": HUMANIZED_PROMPT,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return f"Model error: HTTP {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "Ollama server offline. Run: ollama serve"
    except Exception as e:
        return f" Error: {str(e)}"



if __name__ == "__main__":
    while True:
        q = input("\n❓ You: ")
        print(" Bot:", ask_ollama_with_context(q))


