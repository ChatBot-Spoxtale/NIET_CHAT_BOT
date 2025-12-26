import os, json, requests, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from RAG.Scripts.Facilities.faq import faq_answer_question
from RAG.Scripts.query_rag_bert import answer_question


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

    
def match_syllabus(query: str):
    q = query.lower().strip()

    BEST_FALLBACK = "https://www.niet.co.in/"

    for item in url_chunks:
        aliases = [a.lower().strip() for a in item.get("aliases", [])]
        if any(a in q for a in aliases):
            return item.get("syllabus_url", BEST_FALLBACK)

    for item in url_chunks:
        if item["course"].lower() in q:
            return item.get("syllabus_url", BEST_FALLBACK)

    from difflib import SequenceMatcher
    best_match, best_score = None, 0

    for item in url_chunks:
        score = SequenceMatcher(None, q, item["course"].lower()).ratio()
        if score > best_score:
            best_match, best_score = item, score

    if best_score > 0.45:
        return best_match.get("syllabus_url", BEST_FALLBACK)

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

from difflib import SequenceMatcher

def get_club_answer(q):
    q = q.lower().strip()
    best_answer = None
    best_score = 0

    for item in club_list:
        question_text = item["question"][0].lower()
        score = SequenceMatcher(None, q, question_text).ratio()

        if score > best_score:
            best_score = score
            best_answer = item["answer"][0]

    if best_score > 0.45:
        return best_answer
    return None

def handle_user_query(user_query):
    q = user_query.lower().strip()

    GREETINGS = [
        "hi","hello","hey","namaste","good morning",
        "good evening","good afternoon","whats up","hola","hi there"
    ]

    if any(greet in q for greet in GREETINGS):
        return (
            "Hello! 👋 I'm here to help just like ChatGPT. "
            "Feel free to ask anything — placements, courses, syllabus, hostel, fees, anything you need! 😊"
        )

    rag_answer = answer_question(q)
    return rag_answer

def ask_ollama_with_context(user_query, model="llama3"):
    q = user_query.lower().strip()

    GREETINGS = ["hi","hello","hey","namaste","good morning","good evening","good afternoon","hola"]
    FAQ_KEYWORDS = ["loan","scholarship","uniform","class timing","medium","instruction","canteen","visitors"]
    CLUB_KEYWORDS = ["club","music club","dance club","sports club","cultural club","technical club"]
    RAG_KEYWORDS = ["seat","seats","duration","placement","package","eligibility","documents","admission","fees"]

    if q in GREETINGS:
        return "Hello! 👋 How can I help you today? Ask me anything about NIET. 😊"

    if any(k in q for k in FAQ_KEYWORDS):
        return faq_answer_question(user_query)

    if any(k in q for k in CLUB_KEYWORDS):
        ans = get_club_answer(q)
        if ans:
            return ans

    if any(k in q for k in RAG_KEYWORDS):
        return answer_question(user_query)  

    if "syllabus" in q:
        return match_syllabus(q)

    return run_llm(user_query)


def run_llm(user_query):
    prompt = f"""
You are a friendly ChatGPT-like NIET assistant.

- If message is greeting → greet warmly
- FAQ/club/seat/placement keywords → do not mix responses
- If question is numeric/seat/placement → DO NOT ANSWER, RAG WILL HANDLE
- Do not mix data types. Stay clean.

User: {user_query}
Answer:
"""
    res = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": "llama3", "prompt": prompt},
        stream=True  # <-- IMPORTANT
    )

    full_response = ""
    for line in res.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                full_response += chunk
            except json.JSONDecodeError:
                continue  

    return full_response.strip()
