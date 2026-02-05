import json
import os
import re

# ---------------- LOAD DATA ----------------

BTECH_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data_chunk/course_data_chunk/btech_chunks.json"
)

with open(BTECH_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

BTECH_DATA = raw_data if isinstance(raw_data, list) else [raw_data]

# ---------------- NORMALIZATION ----------------

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\bb\s*\.?\s*tech\b", "btech", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())

# ---------------- BRANCH & SPECIALIZATION MAP ----------------

BRANCH_SIGNALS = {
    "cse": [
        "computer science engineering",
        "computer science",
        "cse"
    ],
    "ece": [
        "electronics and communication",
        "electronics communication",
        "electronics",
        "ece"
    ],
    "it": [
        "information technology",
        "it"
    ],
    "vlsi": [
        "vlsi"
    ],
    "bio": [
        "biotech",
        "biotechnology"
    ],
    "csbs": [
        "csbs",
        "computer science and business systems"
    ],
    "mathematics and computing": [
        "mathematics and computing",
        "mnc"
    ]
}

SPECIALIZATION_SIGNALS = {
    "aiml": ["aiml", "artificial intelligence and machine learning"],
    "ai": ["artificial intelligence"],
    "ds": ["data science"],
    "cyber": ["cyber", "cyber security"],
    "iot": ["iot", "internet of things"],
}

# ---------------- DETECTORS ----------------

def detect_branch(q: str):
    for branch, signals in BRANCH_SIGNALS.items():
        for s in signals:
            if re.search(rf"\b{s}\b", q):
                return branch
    return None


def detect_specializations(q: str):
    found = set()
    for spec, signals in SPECIALIZATION_SIGNALS.items():
        for s in signals:
            if s in q:
                found.add(spec)
    return list(found)


def is_twinning(q: str) -> bool:
    return "twinning" in q or "international" in q


def is_working_professional(q: str) -> bool:
    return "working" in q or "professional" in q


# ---------------- COURSE FILTERS ----------------

def is_btech_course(course: dict) -> bool:
    name = course.get("course", "").lower()
    return (
        "b tech" in name
        and "m tech" not in name
        and "minor" not in name
        and "integrated" not in name
    )


# ---------------- FORMATTERS ----------------

def format_full_course(c: dict) -> str:
    props = c.get("properties", {})
    placements = c.get("placements", {})

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
• Average Package: {placements.get('average', 'NA')}
• Highest Package: {placements.get('highest', 'NA')}
• Details: {placements.get('source_url', 'NA')}

⭐ *Why Choose This Course?*
- """ + "\n- ".join(c.get("why_choose", []))


# ---------------- MAIN ROUTER ----------------

def btech_router(query: str):
    q = normalize(query)

    # 1️⃣ Detect intent
    branch = detect_branch(q)
    specializations = detect_specializations(q)
    twinning = is_twinning(q)
    working = is_working_professional(q)

    if not branch:
        return (
            "Please specify the BTech branch clearly.\n"
            "Example: *BTech CSE AIML placements*"
        )

    
    courses = [
        c for c in BTECH_DATA
        if is_btech_course(c)
        and c.get("branch") == branch
    ]

    if not courses:
        return "No BTech course found for the specified branch."

    # Apply specialization filter
    if specializations:
        filtered = []
        for c in courses:
            spec = normalize(c.get("specialization", ""))
            if any(s in spec for s in specializations):
                filtered.append(c)
        if filtered:
            courses = filtered

    # 4️⃣ Apply program-type filters
    if twinning:
        courses = [
            c for c in courses
            if "twinning" in c.get("course", "").lower()
        ]

    if working:
        courses = [
            c for c in courses
            if "working" in c.get("course", "").lower()
        ]

    if not courses:
        return (
            "No exact BTech course matched your query.\n"
            "Please refine branch or specialization."
        )

    # 5️⃣ Select BEST match
    selected = courses[0]

    props = selected.get("properties", {})
    placements = selected.get("placements", {})

    # 6️⃣ Handle specific questions
    if "seat" in q:
        return f"Seats for {selected.get('course')}: {props.get('seats', 'NA')}"

    if "duration" in q or "year" in q:
        return f"Duration: {props.get('duration', 'NA')}"

    if "eligibility" in q:
        return f"Eligibility: {props.get('eligibility', 'NA')}"

    if "fee" in q:
        return f"Fees: {props.get('fees', 'Check with admission department')}"

    if "placement" in q:
        return (
            f"📊 Placement Details – {selected.get('course')}\n"
            f"- Average Package: {placements.get('average', 'NA')}\n"
            f"- Highest Package: {placements.get('highest', 'NA')}\n"
            f"- More Info: {placements.get('source_url', 'NA')}"
        )

    # 7️⃣ Default: full course info
    return format_full_course(selected)


# ---------------- LOCAL TEST ----------------

if __name__ == "__main__":
    tests = [
        "btech cse ai",
        "btech cse ai twinning",
        "btech it twinning",
        "btech ece vlsi",
        "btech mathematics and computing",
        "btech csbs",
        "btech cse working professionals",
        "btech cse placements"
    ]

    for t in tests:
        print("\nQ:", t)
        print(btech_router(t))
