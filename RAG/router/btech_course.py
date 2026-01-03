# btech_router.py

import json, os, re

BTECH_PATH = os.path.join(os.path.dirname(__file__), "../data/btech_chunks.json")
with open(BTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

BTECH_DATA = data if isinstance(data, list) else [data]

def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r'\bb\.?\s*tech\b', 'btech', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return " ".join(text.split())


BRANCH_ALIASES = {
    "cse": [
        "cse",
        "computer science",
        "computer science engineering"
    ],
    "ece": [
        "ece",
        "electronics",
        "electronics communication",
        "electronics and communication",
        "electronics communication engineering",
        "electronics and communication engineering"
    ],
    "it": [
        "it",
        "information technology",
        "information technology engineering"
    ],
    "me": [
        "me",
        "mechanical",
        "mechanical engineering"
    ],
    "bio": [
        "biotech",
        "biotechnology",
        "biotechnology engineering"
    ],
    "vlsi": [
        "vlsi",
        "vlsi design",
        "vlsi design and technology"
    ],
    "csbs": [
        "csbs",
        "computer science and business systems",
        "business systems"
    ],
}



def btech_router(query: str):
    q = normalize(query)

    if "btech" not in q:
        return None

    best_course = None
    best_score = -1

    for course in BTECH_DATA:
        score = 0
        branch = course.get("branch", "")
        keywords = [normalize(k) for k in course.get("keywords", [])]

        branch_words = BRANCH_ALIASES.get(branch, [])
        if branch_words and not any(b in q for b in branch_words):
            continue  
        course_name = normalize(course.get("course", ""))
        if course_name in q:
            score += 50

        for k in keywords:
            if k == q:
                score += 100
            elif k in q:
                score += 20

        if any(w in q for w in ["overview", "about", "detail", "tell"]):
            score += 5

        if score > best_score:
            best_score = score
            best_course = course

    if not best_course:
        return None

    c = best_course

    if "seat" in q:
        return f"Seats: {c['properties'].get('seats','NA')}"

    if "duration" in q or "year" in q:
        return f"Duration: {c['properties'].get('duration','NA')}"

    if "eligibility" in q:
        return f"Eligibility: {c['properties'].get('eligibility','NA')}"

    if "fee" in q:
        return f"Fees: {c['properties'].get('fees','Check admission dept')}"

    if "placement" in q:
        p = c.get("placements", {})
        return f"""Placement:
• Average: {p.get('average','NA')}
• Highest: {p.get('highest','NA')}
• Source: {p.get('source_url','NA')}
"""

    if any(w in q for w in ["why", "benefit"]):
        return "Why choose this course:\n- " + "\n- ".join(c.get("why_choose", []))

    return c.get("overview", "No overview available.")


def test_btech_router():
    test_queries = [
        # "about btech aiml",
        # " Overview B.Tech-Information Technology",
        # "btech cse aiml placement",
        "Overview B.Tech - Electronics & Communication Engineering"
        # "what is the duration of btech cse aiml",
        # "what is the duration of btech cse ai",
        # "placement record of btech cse ds",
        # "why choose this btech cse ai"
    ]

    print("\n Running B.Tech Router Test Cases:\n")
    for q in test_queries:
        print(f"Query: {q}")
        print(f"Response: {btech_router(q)}\n")


if __name__ == "__main__":
    test_btech_router()
