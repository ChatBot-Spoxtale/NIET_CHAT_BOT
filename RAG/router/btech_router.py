import json
import os
import re

# ---------------- LOAD DATA ----------------

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data_chunk/course_data_chunk/btech_chunks.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

COURSES = DATA if isinstance(DATA, list) else list(DATA.values())


# ---------------- NORMALIZATION ----------------

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\bb\s*\.?\s*tech\b", "btech", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


# ---------------- DETECT QUERY INTENT ----------------

def extract_from_query(query: str):
    q = normalize(query)

    branch = None
    specialization = None
    is_twinning = "twinning" in q or "international" in q
    is_working = "working" in q or "professional" in q

    # branch detection
    for b in ["cse", "ece", "it", "vlsi", "bio", "csbs", "mathematics"]:
        if b in q:
            branch = "mathematics and computing" if b == "mathematics" else b
            break

    # specialization detection
    for s in ["aiml", "ai", "ds", "cyber", "iot"]:
        if s in q:
            specialization = s
            break

    return {
        "query": q,
        "branch": branch,
        "specialization": specialization,
        "twinning": is_twinning,
        "working": is_working,
    }


# ---------------- COURSE FILTER ----------------

def is_valid_btech(course: dict) -> bool:
    return course.get("type") == "btech"


# ---------------- FORMATTERS ----------------

def format_course(course: dict) -> str:
    p = course.get("properties", {})
    pl = course.get("placements", {})

    return f"""
🎓 *{course.get('course')}*

📘 *Overview*
{course.get('overview', 'NA')}

📌 *Course Details*
• Duration: {p.get('duration', 'NA')}
• Seats: {p.get('seats', 'NA')}
• Eligibility: {p.get('eligibility', 'NA')}
• Fees: {p.get('fees', 'NA')}

💼 *Placements*
• Average Package: {pl.get('average', 'NA')}
• Highest Package: {pl.get('highest', 'NA')}
• Details: {pl.get('source_url', 'NA')}

⭐ *Why Choose This Course?*
- """ + "\n- ".join(course.get("why_choose", []))


# ---------------- MAIN ROUTER ----------------

def btech_router(query: str):
    intent = extract_from_query(query)
    q = intent["query"]

    # 1️⃣ Only BTech
    courses = [c for c in COURSES if is_valid_btech(c)]

    if not courses:
        return None

    # 2️⃣ Branch filter
    if intent["branch"]:
        courses = [
            c for c in courses
            if normalize(c.get("branch")) == intent["branch"]
        ]

    if not courses:
        return "No BTech course found for the specified branch."

    # 3️⃣ Specialization filter (IMPORTANT)
    if intent["specialization"]:
        spec_courses = []
        for c in courses:
            spec = normalize(c.get("specialization"))
            if spec == intent["specialization"]:
                spec_courses.append(c)

        if spec_courses:
            courses = spec_courses

    # 4️⃣ Twinning filter
    if intent["twinning"]:
        courses = [
            c for c in courses
            if "twinning" in normalize(c.get("course"))
        ]

    # 5️⃣ Working professional filter
    if intent["working"]:
        courses = [
            c for c in courses
            if "working" in normalize(c.get("course"))
        ]

    if not courses:
        return (
            "No exact BTech course matched your query.\n"
            "Please refine branch or specialization."
        )

    selected = courses[0]
    props = selected.get("properties", {})
    placements = selected.get("placements", {})

    # 6️⃣ Intent-based answers
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
            f"📊 Placement – {selected.get('course')}\n"
            f"- Average: {placements.get('average', 'NA')}\n"
            f"- Highest: {placements.get('highest', 'NA')}\n"
            f"- More Info: {placements.get('source_url', 'NA')}"
        )

    # 7️⃣ Default full response
    return format_course(selected)


# ---------------- LOCAL TEST ----------------

if __name__ == "__main__":
    tests = [
        "btech cse",
        "btech cse aiml",
        "btech cse placements",
        "btech cse aiml placements",
        "btech it fees",
        "btech ece",
    ]

    for t in tests:
        print("\nQ:", t)
        print(btech_router(t))

