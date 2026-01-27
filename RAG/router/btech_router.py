# btech_router.py

import json, os, re

BTECH_PATH = os.path.join(os.path.dirname(__file__), "../data_chunk/course_data_chunk/btech_chunks.json")
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

CSE_SPECIALIZATIONS = {
    "aiml",
    "ai",
    "ds",
    "cy",
    "iot"
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

    branch = detect_branch(q)
    specialization = detect_specialization(q)

    if not branch and specialization in CSE_SPECIALIZATIONS:
        branch="cse"
        
    if not branch:
        return "Please mention the branch like Placement record of btech cse aiml"

    branch_courses = [c for c in BTECH_DATA if c.get("branch") == branch]
    if not branch_courses:
        return None

    selected_course = branch_courses[0]

    if specialization:
        for c in branch_courses:
            if normalize(c.get("specialization", "")) == specialization:
                selected_course = c
                break

    props = selected_course.get("properties", {})
    placements = selected_course.get("placements", {})

    if "seat" in q or "seats" in q:
        return f"Seats for {selected_course.get('course')}: {props.get('seats', 'NA')}"

    if "duration" in q or "year" in q:
        return f"Duration: {props.get('duration', 'NA')}"

    if "eligibility" in q:
        return f"Eligibility: {props.get('eligibility', 'NA')}"

    if "fee" in q or "fees" in q:
        return f"Fees: {props.get('fees', 'Check with admission department')}"

    if "placement" in q:
        return (
            f"- Average Package: {placements.get('average', 'NA')}\n"
            f"- Highest Package: {placements.get('highest', 'NA')}\n"
            f"- Visit For More Information: {placements.get('source_url', 'NA')}"
        )

    return format_full_course(selected_course)

# ---------------- TEST ----------------
if __name__ == "__main__":
    tests = [
        "fees of btech cse",
        "placement of btech cse ai",
        "seats in btech me",
        "overview of btech cse data science",
    ]

    for t in tests:
        print("\nQ:", t)
        print(btech_router(t))

