import os, json, requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FAQ_PATH = os.path.join(BASE_DIR, "RAG", "index_store", "faq_data.json")
CLUB_PATH = os.path.join(BASE_DIR, "RAG", "index_store", "club_data.json")

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    faq_list = json.load(f)

with open(CLUB_PATH, "r", encoding="utf-8") as f:
    club_list = json.load(f)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

formatted_faq = "\n".join([
    f"Q: {item['question'][0]}\nA: {item['answer'][0]}"
    for item in faq_list if "question" in item
])

formatted_club_data = "\n".join([
    f"Q: {item['question'][0]}\nA: {' '.join(item['answer'])}"
    for item in club_list if "question" in item
])

def ask_ollama_with_context(user_query, model="llama3"):
    prompt = f"""
You are a helpful assistant for NIET.
Use the FAQ and CLUB data below to answer correctly.
- If answer exists in data → use it.
- If no exact match → respond normally WITHOUT making up NIET facts.

📌 FAQ DATA:
{formatted_faq}

📌 CLUB DATA:
{formatted_club_data}

User: {user_query}
Answer:
"""
    try:
        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return res.json().get("response", "").strip()
    except Exception as e:
        return f" Ollama Error: {e}"
