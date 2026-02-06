import json, os, re

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data_chunk/course_data_chunk/ug_pg_chunks.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    UGPG_DATA = json.load(f)

def normalize(q: str):
    q = q.lower()
    q = re.sub(r"[^\w\s]", " ", q)
    return " ".join(q.split())

EMPTY_FIELD_WORDS = ["seat","seats","duration","year","years","time","timing"]
COURSE_HINTS = ["mba","mca","bca","bba","integrated"]

def format_ugpg_course(course: dict) -> str:
    p = course.get("placements", {})
    props = course.get("properties", {})

    return f"""
🎓 *{course.get('course')}*

📘 *Overview*
{course.get('overview','NA')}

📌 *Course Details*
• Duration: {props.get('duration','NA')}
• Seats: {props.get('seats','NA')}
• Eligibility: {props.get('eligibility','NA')}
• Fees: {props.get('fees','Check admission department')}

💼 *Placements*
• Average Package: {p.get('average','NA')}
• Highest Package: {p.get('highest','NA')}
• Source: {p.get('source_url','NA')}

⭐ *Why Choose This Course?*
- """ + "\n- ".join(course.get("why_choose", []))

def ug_pg_router(query: str):
    q = normalize(query)


    best_course = None
    best_score = 0

    for data in UGPG_DATA:
        keywords = [normalize(k) for k in data.get("keywords", [])]
        score = 0

        for k in keywords:
            if q == k:
                score += 100

            elif re.search(rf"\b{k}\b", q):
                score += 50

            elif k in q:
                score += 10

        if score > best_score:
            best_score = score
            best_course = data

    if not best_course or best_score < 30:
        return None

    c = best_course


    if any(w in q for w in ["placement", "package", "salary", "highest", "average"]):
        plc = c.get("placements", {})
        return f"""Placement - {c['course']}
• Average Package: {plc.get('average','NA')}
• Highest Package: {plc.get('highest','NA')}
• Source: {plc.get('source_url','NA')}"""

    if any(w in q for w in ["eligibility", "criteria", "qualification", "required", "requirement"]):
        return f"""Eligibility - {c['course']}
{c.get('properties', {}).get('eligibility', 'Not available')}"""

    if "seat" in q or "duration" in q:
        p = c.get("properties", {})
        return f"""{c['course']}
• Seats: {p.get('seats','NA')}
• Duration: {p.get('duration','NA')}"""

    if "fee" in q:
        return f"""Fees - {c['course']}
{c.get('properties', {}).get('fees', 'Check admission department')}"""

    if any(w in q for w in ["why", "benefit", "choose"]):
        reasons = c.get("why_choose", [])
        return f"""Why Choose {c['course']}?
- """ + "\n- ".join(reasons)

    return format_ugpg_course(c)

