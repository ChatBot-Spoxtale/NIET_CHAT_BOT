import os, json, requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FAQ_PATH = os.path.join(BASE_DIR, "RAG", "index_store", "faq_data.json")
CLUB_PATH = os.path.join(BASE_DIR, "RAG", "index_store", "club_data.json")
URLS_DATA_PATH = os.path.join(BASE_DIR, "RAG", "index_store", "url_chunks.json")

with open(FAQ_PATH, "r", encoding="utf-8") as f:
    faq_list = json.load(f)

with open(CLUB_PATH, "r", encoding="utf-8") as f:
    club_list = json.load(f)

with open(URLS_DATA_PATH, "r", encoding="utf-8") as f:
    url_chunks = json.load(f)

    
from difflib import SequenceMatcher

def match_syllabus(query: str):
    q = query.lower().strip()

    BEST_FALLBACK = "https://www.niet.co.in/"

    # 1️⃣ First: Alias detection (strongest)
    for item in url_chunks:
        aliases = [a.lower().strip() for a in item.get("aliases", [])]
        if any(a in q for a in aliases):
            return item.get("syllabus_url", BEST_FALLBACK)

    # 2️⃣ Second: Course name keyword detection
    for item in url_chunks:
        if item["course"].lower() in q:
            return item.get("syllabus_url", BEST_FALLBACK)

    # 3️⃣ Third: Fuzzy similarity (handles spelling mistakes)
    from difflib import SequenceMatcher
    best_match, best_score = None, 0

    for item in url_chunks:
        score = SequenceMatcher(None, q, item["course"].lower()).ratio()
        if score > best_score:
            best_match, best_score = item, score

    if best_score > 0.45:
        return best_match.get("syllabus_url", BEST_FALLBACK)

    # 4️⃣ Default fallback
    return BEST_FALLBACK



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
    q = user_query.lower().strip()

    # 1️⃣ --- SYLLABUS CHECK FIRST (Top Priority) ---
    syllabus = match_syllabus(q)
    if syllabus and syllabus != "https://www.niet.co.in/":
        return syllabus  # return ONLY the PDF link

    # If user asked syllabus but no matching entry found -> fallback
    if "syllabus" in q:
        return "https://www.niet.co.in/"


    # 2️⃣ --- FAQ CHECK ---
    for item in faq_list:
        q_field = item.get("question")
        a_field = item.get("answer")

        if isinstance(q_field, list):
            if q_field[0].lower() in q:
                return a_field[0] if isinstance(a_field, list) else a_field

        elif isinstance(q_field, str):
            if q_field.lower() in q:
                return a_field if isinstance(a_field, str) else a_field[0]


    # 3️⃣ --- CLUB DATA CHECK ---
    for item in club_list:
        q_field = item.get("question")
        a_field = item.get("answer")

        if isinstance(q_field, list) and any(q_val.lower() in q for q_val in q_field):
            return " ".join(a_field) if isinstance(a_field, list) else a_field

        if isinstance(q_field, str) and q_field.lower() in q:
            return " ".join(a_field) if isinstance(a_field, list) else a_field


    prompt = f"""
You are an assistant for NIET. 
When answering, reply directly with the information.
Do NOT say "according to the data" or "as per club data" or "as per url data".
Do NOT explain the source.
Do NOT add disclaimers.
Do NOT mention FAQ or CLUB DATA, URL DATA.
If the answer related syllabus give -> syllabus_url only link 
If the answer exists in the provided data → respond directly.
If not found → say "For more information, Please visit the niet website https://www.niet.co.in/."

URL DATA ,CLUB & FAQ DATA (for reference only, DO NOT MENTION THIS TEXT):
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
