# btech_router.py

import json, os, re

MTECH_PATH = os.path.join(os.path.dirname(__file__), "../data_chunk/course_data_chunk/mtech_chunks.json")
with open(MTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

MTECH_DATA = data if isinstance(data, list) else [data]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[.\-]', ' ', text)  
    return " ".join(text.split())

def format_full_mtech_course(course: dict) -> str:
    p = course.get("placements", {})
    props = course.get("properties", {})

    return f"""
🎓 *{course.get('course')}*

📘 *Overview*
{course.get('overview', 'NA')}

📌 *Course Details*
• Duration: {props.get('duration', 'NA')}
• Seats: {props.get('seats', 'NA')}
• Eligibility: {props.get('eligibility', 'NA')}
• Fees: {props.get('fees', 'Check admission department')}

💼 *Placements*
• Average Package: {p.get('average', 'NA')}
• Highest Package: {p.get('highest', 'NA')}
• Details: {p.get('source_url', 'NA')}

⭐ *Why Choose This Course?*
- """ + "\n- ".join(course.get("why_choose", []))


def mtech_router(query: str):
    q = normalize(query)

    # Accept alternate names for M.Tech
    if not any(word in q for word in [
        "mtech", "m tech", "mtech",
        "master of technology", "master in technology",
        "integrated mtech", "master of integrated technology",
        "integrated technology"
    ]):
        return None

    best_course = None
    best_score = -1

    # ---------- MATCH COURSE ----------
    for course in MTECH_DATA:
        score = 0
        keywords = [normalize(k) for k in course.get("keywords", [])]

        for k in keywords:
            if k == q:
                score += 100
            elif k in q:
                score += 30

        if score > best_score:
            best_score = score
            best_course = course

    if not best_course:
        return None

    c = best_course

    # ---------- SPECIFIC QUESTIONS ----------
    if "seat" in q:
        return f"Seats: {c['properties'].get('seats','Not available')}"

    if "duration" in q or "year" in q:
        return f"Duration: {c['properties'].get('duration','Not available')}"

    if any(w in q for w in ["eligibility","criteria","qualification","required","requirement"]):
        return f"Eligibility: {c['properties'].get('eligibility','Not available')}"

    if "fee" in q:
        return f"Fees: {c['properties'].get('fees','Check admission department')}"

    if "placement" in q or "package" in q:
        p = c.get("placements", {})
        return f"""Placement Statistics:
• Average Package: {p.get('average','NA')}
• Highest Package: {p.get('highest','NA')}
• Official Source: {p.get('source_url','NA')}
"""

    if any(word in q for word in ["why","benefit","advantage","kyu","kyun","kyo"]):
        why = c.get("why_choose", [])
        return (
            "Key Reasons to Choose This Course:\n- "
            + "\n- ".join(why)
            if why else
            "This course offers strong learning, placement, and future career scope."
        )

    if any(word in q for word in ["overview","about","detail","details","tell me","kya hai","kaisa"]):
        return format_full_mtech_course(c)

    # ---------- DEFAULT: FULL DETAILS ----------
    return format_full_mtech_course(c)



def test_mtech_router():
    test_queries = [
        # "about btech aiml",
        " Overview Master of Integrated Technology in Computer Science and Engineering",
        # "btech cse aiml placement",
        # "what is the duration of btech cse aiml",
        # "what is the duration of btech cse ai",
        # "placement record of btech cse ds",
        # "why choose this btech cse ai"
    ]

    for q in test_queries:
        print(f"Query: {q}")
        print(f"Response: {mtech_router(q)}\n")


if __name__ == "__main__":
    test_mtech_router()
