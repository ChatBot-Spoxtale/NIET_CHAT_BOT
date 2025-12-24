import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "admission.json"

def norm(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    synonyms = {
        "upcet": "upcet",
        "upsee": "upcet",
        "jee mains": "jee_mains",
        "jee main": "jee_mains",
        "jee": "jee_mains",

        "direct admission": "direct_admission",
        "management quota": "direct_admission",

        "lateral entry": "lateral_entry",

        "twinning admission": "twinning_admission",
        "international twinning": "twinning_admission",
        "twinning": "twinning_admission",

        "b tech": "btech",
        "btech": "btech",

        "b pharm": "bpharm",
        "bpharm": "bpharm",

        "m tech": "mtech",
        "mtech": "mtech",

        "mba": "mba",
        "mca": "mca",
        "pgdm": "pgdm",

        "first year": "first_year",
        "lateral": "lateral_entry",

        "eligibility": "eligibility",
        "criteria": "eligibility",
        "requirement": "eligibility",
        "requirements": "eligibility",

        "percentage": "marks",
        "percent": "marks",
        "marks": "marks",

        "passport": "passport",
        "ielts": "ielts",
        "visa": "visa",
        "funds": "funds",
    }

    for k, v in synonyms.items():
        text = re.sub(rf"\b{k}\b", v, text)

    return text


def tokenize(text: str):
    return set(norm(text).split())

def match_score(a: str, b: str) -> int:
    return len(tokenize(a) & tokenize(b))

def load():
    with open(KB, encoding="utf-8") as f:
        data=json.load(f)
    return build_admission_chunks(data)

def extract_field(text, field):
    pattern = rf"{field}\s*:\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def build_admission_chunks(data):
    chunks = []
    cid = 1
    data=data.get("Admission_through",{})
    
    counselling = data.get("UPCET_Counseling or JEE mains", {})
    for section, items in counselling.items():
        if isinstance(items, list):
            chunks.append({
                "id": str(cid),
                "category": "UPCET_Counseling or JEE mains",
                "topic": section.replace("_", " ").title(),
                "text": " ".join(items)
            })
            cid += 1

    direct = data.get("Direct_Admission", {})
    for section, items in direct.items():

        if isinstance(items, list) and all(isinstance(i, str) for i in items):
            chunks.append({
                "id": str(cid),
                "category": "Direct_Admission",
                "topic": section.replace("_", " ").title(),
                "text": " ".join(items)
            })
            cid += 1

    twinning = data.get("Twinning_Admission", [])
    chunks.append({
        "id": str(cid),
        "category": "Twinning_Admission",
        "topic": "Requirements",
        "text": " ".join(twinning)
    })

    return chunks

def parse_admission_chunk(chunk):
    if not isinstance(chunk, dict):
        return None

    required_keys = {"id", "category", "topic", "text"}
    if not required_keys.issubset(chunk.keys()):
        return None

    return {
        "id": str(chunk.get("id")),
        "category": str(chunk.get("category", "")),
        "topic": str(chunk.get("topic", "")),
        "text": str(chunk.get("text", ""))
    }

def find_admission(chunks, query):
    best = None
    best_score = 0

    q_norm = norm(query)

    for chunk in chunks:
        parsed = parse_admission_chunk(chunk)
        if not parsed:
            continue

        haystack = f"{parsed['category']} {parsed['topic']} {parsed['text']}"
        score = match_score(q_norm, norm(haystack))

        if score > best_score:
            best_score = score
            best = parsed

    return best if best_score >= 1 else None

def admission_answer(user_query: str):
    chunks = load()
    result = find_admission(chunks, user_query)

    if not result:
        return "Sorry, I could not find information about this facility."
    return (
        f" {result['text']}"
    )    

def demo_from_real_dataset():
    queries = [
        # "What is the eligibility for twinning admission?",
        # "How can I get direct admission?",
        # "Is lateral entry allowed in BTech?",
        # "Admission through JEE mains/Counselling",
        "twinning program",
        "What is the admission process for first year B.Pharm through JEE Main?"
    ]

    for q in queries:
        result = admission_answer(q)

        if result:
            print( result, "...")
        else:
            print("NO MATCH FOUND")


if __name__=="__main__":
    demo_from_real_dataset()    