# query_rag_club.py

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "club_data.json"

with open(KB, "r", encoding="utf-8") as f:
    club_data = json.load(f)

STOP_WORDS = {
    "what", "tell", "about", "is", "are", "the", "of", "in", "on",
    "ka", "ki", "ke", "me", "hai", "kya", "list", "details"
}

SYNONYMS = {
    "society": "club",
    "team": "club",
    "groups": "club",
    "niet": ""
}

def normalize(text: str) -> str:
    text = text.lower()
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

def query_rag_club(user_query: str) -> str:
    query_norm = normalize(user_query)

    best_match = None
    best_score = 0

    for item in club_data:
        for q in item.get("question", []):
            q_norm = normalize(q)

            score = len(set(query_norm.split()) & set(q_norm.split()))

            if score > best_score:
                best_score = score
                best_match = item

    if best_match is None or best_score < 1:
        return "I don't know based on the available club information."

    return " ".join(best_match.get("answer", []))

# ---------------- TEST ----------------
if __name__ == "__main__":
    tests = [
        # "niet me dance club",
        # "nritya bhakti kya hai",
        # "list clubs",
        # "yoga club hai kya",
        # "tell me about spectrum",
        # "photography club",
        # "random question",
        "aim of chess club"
    ]

    for t in tests:
        print("Q:", t)
        print("A:", query_rag_club(t))
        print("-" * 70)
