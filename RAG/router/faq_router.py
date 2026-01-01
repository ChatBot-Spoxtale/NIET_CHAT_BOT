import json, os, re

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/combined_chunks.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)


BLOCK_KEYWORDS = [
    "admission","jee","jee main","uptu","uptac","aktu","counselling",
    "btech","b tech","course","branch","why choose","overview",
    "syllabus","subject","club","mba","mca","mtech","eligibility",
    "average package","placement","highest package"
]


SAFE_KEYWORDS = [
    "wifi","geyser","non veg","non-veg","food","mess","laundry","washing machine",
    "coffee","tea","breakfast","dinner","lunch","transport","bus","hostel","room",
    "almirah","study table","furniture","water","drinking water","chair","bed"
]


STOPWORDS = set([
    "is","in","on","at","to","for","of","the","a","an","how","what","when",
    "why","who","where","can","do","does","about","available","from","you"
])


def clean(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9 ]', '', text.lower()).strip()


def keyword_faq_router(query: str):
    q = clean(query)

    if any(b in q for b in BLOCK_KEYWORDS):
        return None

    if any(s in q for s in SAFE_KEYWORDS):
        for item in FAQ_DATA:
            if any(s in clean(item["question"]) for s in SAFE_KEYWORDS if s in q):
                return item["answer"]

    for item in FAQ_DATA:
        if "keywords" in item:
            for kw in item["keywords"]:
                if kw in q:
                    return item["answer"]

    filtered = [w for w in q.split() if w not in STOPWORDS]
    for item in FAQ_DATA:
        if any(w in clean(item["question"]) for w in filtered):
            return item["answer"]

    return "I don't have info for that. Please be specific."


def format_faq(item):
    return f"""
Keyword Matched: {item['question']}
{item['answer']}
"""


# TEST
if __name__ == "__main__":
    print(keyword_faq_router("non veg"))
    print(keyword_faq_router("wifi hostel"))
    print(keyword_faq_router("coffee"))
    print(keyword_faq_router("transport"))
