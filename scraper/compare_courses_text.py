import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
KB = BASE / "data" / "base_knowledge.json"

def norm(x):
    return x.lower().replace("&", "and").replace("-", " ")

def load():
    return json.load(open(KB, encoding="utf-8"))

def find_course(kb, name):
    q = norm(name)
    for c in kb["courses"].values():
        if q in norm(c["course_name"]):
            return c
    return None

def fmt(v):
    return v if v else "Not Available"

def join_list(x):
    if isinstance(x, list):
        return ", ".join(x[:3])
    if isinstance(x, dict):
        return "; ".join(x.get("content", [])[:3])
    return fmt(x)

def compare_courses_text(course1, course2):
    kb = load()
    c1 = find_course(kb, course1)
    c2 = find_course(kb, course2)

    if not c1 or not c2:
        return "Sorry, I could not find one or both courses to compare."

    lines = []

    lines.append(f"Course Comparison: {c1['course_name']} vs {c2['course_name']}")
    lines.append("")

    lines.append("Duration:")
    lines.append(f"{c1['course_name']}: {fmt(c1.get('duration'))}")
    lines.append(f"{c2['course_name']}: {fmt(c2.get('duration'))}")
    lines.append("")

    lines.append("Seats:")
    lines.append(f"{c1['course_name']}: {fmt(c1.get('seats'))}")
    lines.append(f"{c2['course_name']}: {fmt(c2.get('seats'))}")
    lines.append("")

    lines.append("Fees:")
    lines.append(f"{c1['course_name']}: {fmt(c1.get('fees'))}")
    lines.append(f"{c2['course_name']}: {fmt(c2.get('fees'))}")
    lines.append("")

    lines.append(f"Why choose {c1['course_name']}:")
    lines.append(join_list(c1.get("why_choose")))
    lines.append("")

    lines.append(f"Why choose {c2['course_name']}:")
    lines.append(join_list(c2.get("why_choose")))
    lines.append("")

    lines.append("Syllabus Highlights:")
    lines.append(f"{c1['course_name']}: {join_list(c1.get('syllabus'))}")
    lines.append(f"{c2['course_name']}: {join_list(c2.get('syllabus'))}")

    return "\n".join(lines)
