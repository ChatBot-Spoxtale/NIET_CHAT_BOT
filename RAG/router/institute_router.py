import json
import re
from pathlib import Path
from typing import Optional
from llm_model_gemini.chat import chat

# ---------------- Paths ----------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data_chunk" / "institute_data_chunk" / "institute_chunks.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    INSTITUTE_DATA = json.load(f)


# ---------------- Helpers ----------------

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


INSTITUTE_KEYWORDS = [
    "niet",
    "college",
    "about",
    "overview",
    "award",
    "awards",
    "ranking",
    "rankings",
    "nirf",
    "accreditation",
    "naac",
    "nba",
    "collaboration",
    "international",
    "alliances",
]


# ---------------- Router ----------------

def institute_router(query: str) -> Optional[str]:
    q = normalize(query)

    # Fast intent check
    if not any(k in q for k in INSTITUTE_KEYWORDS):
        return None

    best_match = None
    best_score = 0

    for item in INSTITUTE_DATA:
        keywords = item.get("keywords", [])
        score = sum(1 for kw in keywords if kw in q)

        if score > best_score:
            best_score = score
            best_match = item

    if best_match:
        return best_match.get("answer")

    # Safe fallback

    try:
        llm_answer = chat(query)
        return (
            f"{llm_answer}\n\n"
            "🔗 For official and up-to-date institute information, "
            "please visit our website:\n"
            "https://www.niet.co.in/"
        )
    except Exception as e:
        print("Institute LLM failed:", e)
        return (
            "For official and up-to-date institute information, "
            "please visit our website:\n"
            "https://www.niet.co.in/"
        )
