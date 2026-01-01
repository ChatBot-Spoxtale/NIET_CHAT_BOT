# RAG/routers/course_router.py

from difflib import get_close_matches
import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "../data/courses_chunks.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    content = f.read().strip()
    if not content:
        raise ValueError("JSON FILE IS EMPTY!")
    RAW_DATA = json.loads(content)

SEAT_DATA = RAW_DATA[0]["seat_data"]
DURATION_DATA = RAW_DATA[1]["duration_data"]
WHY_CHOOSE_DATA = RAW_DATA[2]["why_choose"]

CATEGORY_MAP = {
    "seat": ["seats", "intake", "kitna", "kitne", "how many","seets"],
    "duration": ["duration", "years", "kitne saal", "time period", "course time"],
    "why": ["why choose", "benefits", "kyu", "kyo", "scope", "future"]
}

def detect_category(q):
    for key, triggers in CATEGORY_MAP.items():
        if any(t in q for t in triggers):
            return key
    return None  

def fuzzy_search(query, dataset):
    q = query.lower()
    all_keywords = [kw for item in dataset for kw in item["keywords"]]
    close = get_close_matches(q, all_keywords, n=1, cutoff=0.5)
    
    if close:
        match = close[0]
        for item in dataset:
            if match in item["keywords"]:
                return item

    return None

def course_router(query: str):
    q = query.lower().strip()
    category = detect_category(q)

    if category == "seat":
        item = fuzzy_search(q, SEAT_DATA)
        if item: return f"{item['course']} Seats: {item['seats']}"
        return " No seat data found for this query."

    if category == "duration":
        item = fuzzy_search(q, DURATION_DATA)
        if item: return f"{item['course']} Duration: {item['duration']}"
        return "Duration not available."

    if category == "why":
        item = fuzzy_search(q, WHY_CHOOSE_DATA)
        if item:
            reasons = "\n- " + "\n- ".join(item["reasons"])
            return f"Why choose {item['course']}{reasons}"
        return " No why-choose info found."

    return " I found nothing. Check spelling or ask like:\n- btech cse seats\n- bca duration\n- why choose aiml"


if __name__ == "__main__":
    queries = [
        "btech csbs seat",
        "duration of bca",
        "why choose cyber security",
        "aiml seets",     
        "cse datta science scope"
    ]
    for q in queries:
        print(course_router(q))
