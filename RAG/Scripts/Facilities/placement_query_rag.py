# placement_query.py

import json
import re
from pathlib import Path

# ---------------- PATH ----------------
BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "placement_chunks.json"

with open(KB, "r", encoding="utf-8") as f:
    placement_data = json.load(f)

# ---------------- CONFIG ----------------
STOP_WORDS = {
    "what", "is", "are", "the", "of", "in", "on", "package", "placement",
    "placements", "highest", "average", "record", "details",
    "ka", "ki", "ke", "me", "hai", "kya"
}

# Similar course mapping (IMPORTANT)
COURSE_ALIASES = {
    "aiml": ["artificial intelligence", "machine learning", "aiml","twinning aiml"],
    "ai": ["artificial intelligence", "aiml"],
    "data science": ["data science",  "computer science"],
    "cse": ["computer science engineering", "computer science"],
    "cs": ["computer science"],
    "it": ["information technology"],
    "mba":["mba","mba bba","mba+bba"]
}

# ---------------- NORMALIZATION ----------------
def normalize(text: str) -> str:
    if text is None:
        return ""
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = []
    for w in text.split():
        if w not in STOP_WORDS:
            words.append(w)
    return " ".join(words)

# ---------------- FIND SIMILAR DEPARTMENTS ----------------
def get_target_departments(query: str):
    query = normalize(query)

    matched_departments = set()

    for key, aliases in COURSE_ALIASES.items():
        if key in query:
            matched_departments.update(aliases)

    # fallback: use words directly
    if not matched_departments:
        matched_departments.add(query)

    return matched_departments

# ---------------- MAIN QUERY FUNCTION ----------------
def query_placement(user_query: str) -> str:
    targets = get_target_departments(user_query)

    results = {}
    department_name = None
    source_url = None

    for item in placement_data:
        dept_norm = normalize(item["department"])

        for target in targets:
            if target in dept_norm:
                department_name = item["department"]
                results[item["metric"]] = item["value"]
                source_url = item["url"]

    if not results:
        return "I don't know based on the available placement information."

    response_lines = [
        f"Placement Record for {department_name}:",
    ]

    if "placements_offered" in results:
        response_lines.append(f"• Placements Offered: {results['placements_offered']}")

    if "highest_package" in results:
        response_lines.append(f"• Highest Package: {results['highest_package']}")

    if "average_package" in results:
        response_lines.append(f"• Average Package: {results['average_package']}")

    if source_url:
        response_lines.append(f"\n🔗 Source: {source_url}")

    return "\n".join(response_lines)


# ---------------- TEST ----------------
if __name__ == "__main__":
    tests = [
        "placement record of aiml",
        "ai highest package",
        "data science placement",
        "computer science placement details",
        "mechanical engineering placements",
        "random question"
    ]

    for q in tests:
        print("Q:", q)
        print("A:", query_placement(q))
        print("-" * 80)
