# overview_course_query.py

import json
import re
from pathlib import Path

# ---------------- PATHS ----------------
BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "overview_metadata.json"

with open(KB, "r", encoding="utf-8") as f:
    course_data = json.load(f)

# ---------------- CONFIG ----------------
STOP_WORDS = {
    "what", "is", "are", "the", "of", "in", "on", "about", "tell",
    "course", "program", "details",
    "ka", "ki", "ke", "me", "hai", "kya"
}

SYNONYMS = {
    "btech": "b tech",
    "cse": "computer science",
    "aiml": "artificial intelligence machine learning",
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "it": "information technology",
    "niet": "",
}

# ---------------- NORMALIZATION ----------------
def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = []
    for word in text.split():
        if word in STOP_WORDS:
            continue
        word = SYNONYMS.get(word, word)
        if word:
            words.append(word)

    return " ".join(words)

# ---------------- QUERY FUNCTION ----------------
def overview_course_query(user_query: str) -> str:
    query_norm = normalize(user_query)

    best_match = None
    best_score = 0

    for item in course_data:
        slug_norm = normalize(item["course_slug"])
        text_norm = normalize(item["text"])

        slug_score = len(set(query_norm.split()) & set(slug_norm.split()))
        text_score = len(set(query_norm.split()) & set(text_norm.split()))

        total_score = slug_score * 2 + text_score  # slug has higher weight

        if total_score > best_score:
            best_score = total_score
            best_match = item

    if best_match is None or best_score < 2:
        return "I don't know based on the available course information."

    return best_match["text"]

# ---------------- TESTS ----------------
if __name__ == "__main__":
    tests = [
        "what is btech cse",
        "tell me about aiml course",
        "cloud computing btech",
        "is data science available",
        "vlsi course details",
        "mechanical engineering overview",
        "mba program",
        "quantum computing course",
        "random unrelated question"
    ]

    for t in tests:
        print("Q:", t)
        print("A:", overview_course_query(t))
        print("-" * 80)
