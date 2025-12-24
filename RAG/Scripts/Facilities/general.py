import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "hostel_facilities.json"

def norm(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    synonyms = {
        "non veg": "Non_veg",
        "non-veg": "Non_veg",
        "nonveg":"Non_veg",
        "non veg meals":"Non_veg",

        "breakfast": "Breakfast",
        "BREAKFAST": "Breakfast",

        "Dinners": "Dinner",
        "dinner": "Dinner",

        "lunch": "Lunch",
        "lunchs": "Lunch",

        "chai": "Tea",
        "tea": "Tea",

        "coffee": "Coffee",
        "COFFEE": "Coffee",
        "washing machine": "Washing Machine",
        "Washing machine": "Washing Machine",
        "Washing clothes":"Washing Machine",

        "iron":"Iron",  
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

def parse_general_chunk(chunk):
    if not isinstance(chunk, dict):
        return None

    if not all(k in chunk for k in ("id", "category", "topic", "text")):
        return None

    return {
        "id": chunk["id"],
        "category": chunk["category"],
        "topic": chunk["topic"],
        "text": chunk["text"]
    }

def find_general(chunks, query):
    best = None
    best_score = 0

    q_norm = norm(query)

    for chunk in chunks:
        parsed = parse_general_chunk(chunk)
        if not parsed:
            continue

        topic = norm(parsed["topic"])
        text = norm(parsed["text"])

        if topic in q_norm or q_norm in topic:
            return parsed

        haystack = f"{parsed['topic']} {parsed['category']} {parsed['text']}"
        score = match_score(q_norm, haystack)

        if score > best_score:
            best_score = score
            best = parsed

    return best if best_score >= 2 else None



def general_answer(user_query: str):
    chunks = load()
    result = find_general(chunks, user_query)

    if not result:
        return "Sorry, I could not find information about this facility."
    return (
        f" {result['text']}"
    )


def demo_test():
    test_queries = [
    # -------- FOOD --------
    "Is non veg food available in hostel?",
    "Do hostels provide non veg meals?",
    "Is non-veg allowed in NIET hostel?",
    "Can students eat non veg in hostel?",
    
    "Is breakfast available daily in hostel?",
    "Do we get lunch and dinner every day?",
    "Breakfast, lunch and dinner available or not?",
    "Are all meals provided in hostel mess?",
    "Hostel mess food available all day?",

    "Is tea available in hostel mess?",
    "Do we get coffee in the morning?",
    "Tea or coffee available in hostel?",
    "Chai milti hai hostel mess me?",

    # -------- LAUNDRY --------
    "Is washing machine available in hostel?",
    "Do hostels provide washing machine facility?",
    "Washing clothes facility available?",
    "Hostel me washing machine hai?",
    "Laundry service available in hostel?",

    "Is iron provided by hostel?",
    "Iron allowed or not?",
    "Can I use iron in hostel?",
    "Do hostels give iron for clothes?",

    # -------- GENERAL / MIXED --------
    "What food facilities are available in hostel?",
    "Hostel facilities related to food",
    "Mess facilities in NIET hostel",
    "Hostel laundry facilities?",
    "Facilities available for hostel students",

    # -------- EDGE / INTERVIEW LEVEL --------
    "Is dinner compulsory in hostel?",
    "Breakfast timing in hostel?",
    "Are tea and coffee free?",
    "Washing machine free or paid?",
    "Iron allowed inside hostel rooms?"


    "Is non veg food available in hostel?",
    "Do hostel rooms have bed and almirah?",
    "Is WiFi available in hostel?",
    "RO water available in hostel?",
    "Is geyser facility provided?",
    "Iron allowed in hostel?",
    "Washing clothes facility available?"

    ]


    for q in test_queries:
        print(f"Query: {q}")
        print(general_answer(q))
        print("-" * 50)

if __name__ == "__main__":
    demo_test()
