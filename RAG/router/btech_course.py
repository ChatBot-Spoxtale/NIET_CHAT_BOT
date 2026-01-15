# btech_router.py

import json, os, re

BTECH_PATH = os.path.join(os.path.dirname(__file__), "../data/btech_chunks.json")
with open(BTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

BTECH_DATA = data if isinstance(data, list) else [data]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\bb\s*\.?\s*tech\b", "btech", text)   
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

def detect_branch(q: str):
    q = q.lower()
    for branch, signals in BRANCH_SIGNALS.items():
        for s in signals:
            if re.search(rf"\b{s}\b", q):
                return branch
    return None
def normalize_branch(branch: str):
    for key, aliases in BRANCH_ALIASES.items():
        for a in aliases:
            if a in branch:
                return key
    return branch


def detect_specialization(q: str):
    for spec, signals in SPECIALIZATION_SIGNALS.items():
        for s in signals:
            if s in q:
                return spec
    return None

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

SPECIALIZATION_MAP = {
    "aiml": ["aiml", "artificial intelligence and machine learning"],
    "ai": ["ai", "artificial intelligence"],
    "ds": ["data science"],
    "cy": ["cyber", "cyber security"],
    "iot": ["iot", "internet of things"]
}

BRANCH_SIGNALS = {
    "cse": ["computer science", "cse"],
    "cs": ["computer science", "cs"],
    "ece": ["electronics", "electronics and communication", "ece"],
    "vlsi": ["vlsi", "vlsi design", "vlsi design and technology"],
    "it": ["information technology", "it"],
    "me": ["mechanical", "mechanical engineering"],
    "bio": ["biotechnology"],
    "bca": ["bca", "bachelor of computer applications"],
    "csbs": ["computer science and business systems", "csbs"],
    "mathematics and computing": ["mathematics and computing", "mnc", "math computing"]
}

SPECIALIZATION_SIGNALS = {
    "aiml": ["aiml", "artificial intelligence and machine learning"],
    "ai": ["artificial intelligence"],
    "ds": ["data science"],
    "cy": ["cyber", "cyber security"],
    "iot": ["iot", "internet of things"],
    "twinning": ["twinning", "international"],
    "aiml twinning": ["aiml twinning", "international twinning"]
}

def format_full_course(c: dict) -> str:
    p = c.get("placements", {})
    props = c.get("properties", {})

    return f"""
🎓 *{c.get('course')}*

📘 *Overview*
{c.get('overview', 'NA')}

📌 *Course Details*
• Duration: {props.get('duration', 'NA')}
• Seats: {props.get('seats', 'NA')}
• Eligibility: {props.get('eligibility', 'NA')}
• Fees: {props.get('fees', 'NA')}

💼 *Placements*
• Average Package: {p.get('average', 'NA')}
• Highest Package: {p.get('highest', 'NA')}
• Details: {p.get('source_url', 'NA')}

⭐ *Why Choose This Course?*
- """ + "\n- ".join(c.get("why_choose", []))


def btech_router(query: str):
    q = normalize(query)
    # current_course = BTECH_DATA[0] if BTECH_DATA else None
    selected_course = None

    if not any(k in q for k in ["btech", "seat", "seats", "placement", "duration", "eligibility", "fee"]):
        return None


    if "::" in query:
        parts = query.lower().split("::")
        _, branch, *spec = parts
        specialization = spec[0] if spec else ""

        for c in BTECH_DATA:
            if c.get("branch") == branch:
                if specialization:
                    if normalize(c.get("specialization", "")) == specialization:
                        return format_full_course(c)
                else:
                    return format_full_course(c)

    branch = detect_branch(q)
    specialization = detect_specialization(q)
    
    if branch:
        branch_courses = [
            c for c in BTECH_DATA if c.get("branch") == branch
        ]
        if branch_courses:
            selected_course = branch_courses[0]
        if specialization:
            for c in branch_courses:
                if normalize(c.get("specialization", "")) == specialization:
                    return format_full_course(c)

        for c in branch_courses:
            if not c.get("specialization") or c.get("specialization").strip() == "":
                return format_full_course(c)

        if branch_courses:
            return format_full_course(branch_courses[0])


    if "seat" in q:
        return f"Seats: {selected_course['properties'].get('seats','NA')}"

    if "duration" in q or "year" in q:
        return f"Duration: {selected_course['properties'].get('duration','NA')}"

    if "eligibility" in q:
        return f"Eligibility: {selected_course['properties'].get('eligibility','NA')}"

    if "fee" in q:
        return f"Fees: {selected_course['properties'].get('fees','Check admission dept')}"

    if "placement" in q:
        if not selected_course:
            return "Detailed placement statistics for branch are individually published in the official placement records. Visit to the institute’s placement overview at https://www.niet.co.in/placement/placement-records";

        p = selected_course.get("placements", {})
        return f"""Placement:
• Average: {p.get('average','NA')}
• Highest: {p.get('highest','NA')}
• Source: {p.get('source_url','NA')}
"""

    if any(w in q for w in ["why", "benefit"]):
        return "Why choose this course:\n- " + "\n- ".join(c.get("why_choose", []))

    return format_full_course(c)


def test_btech_router():
    test_queries = [
        # "about btech aiml",
        # " Overview B.Tech-Information Technology",
        # "btech cse aiml placement",
    "Overview B.Tech CSE Data Science"
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
