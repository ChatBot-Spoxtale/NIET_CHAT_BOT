# mtech_router.py

import json, os, re

# ---------------- LOAD DATA ----------------
MTECH_PATH = os.path.join(os.path.dirname(__file__), "../data/mtech_chunks.json")
with open(MTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

MTECH_DATA = data if isinstance(data, list) else [data]

# ---------------- HELPERS ----------------
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\bm\s*\.?\s*tech\b", "mtech", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

def detect_branch(q: str):
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

# ---------------- FORMATTER ----------------
def format_full_mtech_course(c: dict) -> str:
    p = c.get("placements", {})
    props = c.get("properties", {})

    return f"""
 *{c.get('course')}*

 *Overview*
{c.get('overview', 'NA')}

*Course Details*
- Duration: {props.get('duration', 'NA')}
- Seats: {props.get('seats', 'NA')}
- Eligibility: {props.get('eligibility', 'NA')}
- Fees: {props.get('fees', 'Check admission department')}

 *Placements*
- Average Package: {p.get('average', 'NA')}
- Highest Package: {p.get('highest', 'NA')}
- Details: {p.get('source_url', 'NA')}

 *Why Choose This Course?*
- """ + "\n- ".join(c.get("why_choose", []))

# ---------------- ROUTER ----------------
def mtech_router(query: str):
    q = normalize(query)

    # STRICT trigger: only M.Tech queries
    if not any(k in q for k in ["mtech", "m tech", "master of technology"]):
        return None

    is_integrated = "integrated" in q

    branch = detect_branch(q)
    specialization = detect_specialization(q)

    if not branch:
        return "Please mention the branch clearly, for example: mtech cse aiml"

    branch_courses = [
        c for c in MTECH_DATA
        if c.get("branch") == branch
        and (
            (is_integrated and c.get("program_type") == "integrated")
            or (not is_integrated and c.get("program_type") != "integrated")
        )
    ]

    if not branch_courses:
        return (
            "NIET offers both Regular (2 Years) and Integrated (5 Years) M.Tech programs.\n\n"
            "Please specify clearly:\n"
            "- M.Tech CSE AI/ML\n"
            "- Integrated M.Tech CSE AI/ML\n\n"
            "For official details visit:\nhttps://www.niet.co.in"
        )

    selected_course = branch_courses[0]

    if specialization:
        for c in branch_courses:
            if normalize(c.get("specialization", "")) == specialization:
                selected_course = c
                break

    props = selected_course.get("properties", {})
    placements = selected_course.get("placements", {})

    if "seat" in q or "seats" in q:
        return f"Seats: {props.get('seats', 'NA')}"

    if "duration" in q or "year" in q:
        return f"Duration: {props.get('duration', 'NA')}"

    if any(w in q for w in ["eligibility", "criteria", "qualification"]):
        return f"Eligibility: {props.get('eligibility', 'NA')}"

    if "fee" in q or "fees" in q:
        return f"Fees: {props.get('fees', 'Check admission department')}"

    if "placement" in q or "package" in q:
        return (
            f"*Placements for {selected_course.get('course')}*\n"
            f"- Average Package: {placements.get('average', 'NA')}\n"
            f"- Highest Package: {placements.get('highest', 'NA')}\n"
            f"- Details: {placements.get('source_url', 'NA')}"
        )

    return format_full_mtech_course(selected_course)

# ---------------- TEST ----------------
if __name__ == "__main__":
    tests = [
        "fees of mtech cse",
        "placement of mtech cse ai",
        "seats in mtech me",
        "overview of mtech cse data science",
    ]

    for t in tests:
        print("\nQ:", t)
        print(mtech_router(t))
