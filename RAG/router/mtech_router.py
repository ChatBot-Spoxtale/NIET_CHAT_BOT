import json, os, re

# ---------------- LOAD DATA ----------------
MTECH_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data_chunk/course_data_chunk/mtech_chunks.json"
)

with open(MTECH_PATH, "r", encoding="utf-8") as f:
    MTECH_DATA = json.load(f)

# ---------------- HELPERS ----------------
def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def extract_mtech_intent(q: str):
    intent = {
        "branch": None,
        "specialization": None
    }

    # -------- BRANCH DETECTION --------
    if "computer science" in q or "cse" in q:
        intent["branch"] = "cse"
    elif "mechanical" in q or " me " in f" {q} ":
        intent["branch"] = "me"
    elif "artificial intelligence" in q or " ai " in f" {q} ":
        intent["branch"] = "ai"
    elif "vlsi" in q:
        intent["branch"] = "vlsi design"
    elif "biotech" in q or "biotechnology" in q:
        intent["branch"] = "biotechnology"

    # -------- SPECIALIZATION --------
    if "working professional" in q or "working professionals" in q:
        intent["specialization"] = "working professionals"
    elif "integrated" in q:
        intent["specialization"] = "integrated"

    return intent


def format_full_mtech_course(c: dict) -> str:
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


def mtech_router(query: str):
    q = normalize(query)

    if not any(k in q for k in [
        "mtech", "m tech", "master of technology",
        "integrated mtech", "integrated technology"
    ]):
        return None

    intent = extract_mtech_intent(q)
    best_course = None

    if intent["branch"] and intent["specialization"]:
        for c in MTECH_DATA:
            if (
                c.get("type") == "mtech"
                and c.get("branch") == intent["branch"]
                and c.get("specialization") == intent["specialization"]
            ):
                best_course = c
                break

    if not best_course and intent["branch"]:
        for c in MTECH_DATA:
            if c.get("type") == "mtech" and c.get("branch") == intent["branch"]:
                best_course = c
                break

    if not best_course:
        best_score = -1
        for c in MTECH_DATA:
            score = 0
            for kw in map(normalize, c.get("keywords", [])):
                if kw == q:
                    score += 100
                elif kw in q:
                    score += 30
            if score > best_score:
                best_score = score
                best_course = c

    if not best_course:
        return None

    c = best_course

    if "seat" in q:
        return f"Seats: {c['properties'].get('seats','Not available')}"

    if "duration" in q or "year" in q:
        return f"Duration: {c['properties'].get('duration','Not available')}"

    if any(w in q for w in ["eligibility","criteria","qualification","required"]):
        return f"Eligibility: {c['properties'].get('eligibility','Not available')}"

    if "fee" in q:
        return f"Fees: {c['properties'].get('fees','Check admission department')}"

    if "placement" in q or "package" in q:
        p = c.get("placements", {})
        return (
            f"Placements:\n"
            f"Average Package: {p.get('average','NA')}\n"
            f"Highest Package: {p.get('highest','NA')}\n"
            f"Source: {p.get('source_url','NA')}"
        )

    if any(w in q for w in ["why","benefit","advantage","kyu","kyun","kyo"]):
        return (
            "Why Choose This Course:\n- "
            + "\n- ".join(c.get("why_choose", []))
        )

    if any(w in q for w in ["overview","about","detail","details","tell me"]):
        return format_full_mtech_course(c)

    return format_full_mtech_course(c)