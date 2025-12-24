import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "metadata.json"

def norm(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    synonyms = {
        "classroom": "classrooms",
        "classrooms": "classrooms",
        "Classrooms":"classrooms",
        "Classroom Facilities":"classrooms",
        "niet classrooms":"classrooms",

        "library": "library",
        "libraries": "library",

        "lab": "laboratories",
        "labs": "laboratories",
        "laboratory": "laboratories",

        "medical": "medical help",
        "medical support": "medical help",

        "admission": "admission help",
        "admission support": "admission help",

        "transport": "transporation",
        "transportation": "transporation",
        "bus": "transporation",
        "buses": "transporation",
    }

    for k, v in synonyms.items():
        text = text.replace(k, v)

    return text.strip()

def tokenize(text: str):
    return set(norm(text).split())

def match_score(a: str, b: str) -> int:
    return len(tokenize(a) & tokenize(b))

def load():
    with open(KB, encoding="utf-8") as f:
        return json.load(f)

def extract_field(text, field):
    pattern = rf"{field}\s*:\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def parse_facility_chunk(chunk):
    text = chunk["text"]

    if not text.startswith("Facility:"):
        return None

    facility = extract_field(text, "Facility")
    category = extract_field(text, "Category")
    description = extract_field(text, "Description")

    return {
        "facility": facility,
        "category": category,
        "description": description,
    }


def find_facility(chunks, query):
    best = None
    best_score = 0

    q_norm = norm(query)

    for chunk in chunks:
        parsed = parse_facility_chunk(chunk)
        if not parsed:
            continue

        haystack = f"{parsed['facility']} {parsed['category']}"

        score = match_score(q_norm, haystack)

        if score > best_score:
            best_score = score
            best = parsed

    return best if best_score >= 1 else None


def facility_answer(user_query: str):
    chunks = load()
    result = find_facility(chunks, user_query)

    if not result:
        return "Sorry, I could not find information about this facility."
    return (
        # f"{result['facility']}\n"
        # f"{result['category']}\n\n"
        f"Yes, {result['description']}"
    )


def demo_test():
    test_queries = [
        # "how was the transportation of NIET",
        # "is bus facility available",
        # "tell me about library",
        # "medical support in campus",
        # "admission help number",
        "is lab are available in niet",
        # "classroom facilities",
        # "Classroom",
        # "tell me about hostel features of niet",
        # "what about the auditorium hall in niet",
        "what about niet classroom"
    ]

    for q in test_queries:
        print(f"Query: {q}")
        print(facility_answer(q))
        print("-" * 50)

if __name__ == "__main__":
    demo_test()
