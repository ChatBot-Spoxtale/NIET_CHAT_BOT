import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "metadata.json"


# Utilities 

def norm(x: str) -> str:
    x = x.lower()
    x = x.replace("&", "and")
    x = x.replace("-", " ")
    x = x.replace(".", "")
    x = re.sub(r"\s+", " ", x)

    x = x.replace("btech", "b tech")
    x = x.replace("b.tech", "b tech")
    x = x.replace("cse", "computer science")
    x = x.replace("ai", "artifical intelligence")
    x = x.replace("aiml", "artifical intelligence and machine learning")


    x = x.replace("bba", "bachelor of business administration")
    x = x.replace("mba", "master of business administration")
    x = x.replace("mca", "master of computer applications")
    return x.strip()


def tokenize(text: str) -> set:
    return set(norm(text).split())


def match_score(a: str, b: str) -> int:
    return len(tokenize(a) & tokenize(b))


def load():
    with open(KB, encoding="utf-8") as f:
        return json.load(f)


def extract_field(text, field):
    pattern = rf"{field}\s*:\s*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Not Available"


def parse_course_chunk(chunk):
    text = chunk["text"]

    if "course name" not in text.lower():
        return None

    return {
        "course_name": extract_field(text, "Course Name"),
        "duration": extract_field(text, "Duration"),
        "mode": extract_field(text, "Mode"),
        "seats": extract_field(text, "Seats"),
        "placements":extract_field(text,"Placements")
    }


def find_course(chunks, name):
    best = None
    best_score = 0

    for chunk in chunks:
        parsed = parse_course_chunk(chunk)
        if not parsed:
            continue

        score = match_score(name, parsed["course_name"])

        if score > best_score:
            best_score = score
            best = parsed

    return best if best_score >= 2 else None


def compare_courses_text(course1, course2):
    chunks = load()

    c1 = find_course(chunks, course1)
    c2 = find_course(chunks, course2)

    if not c1 or not c2:
        return "Sorry, I could not find one or both courses."

    lines = []
    lines.append(f"Course Comparison: {c1['course_name']} vs {c2['course_name']}")
    lines.append("")
    lines.append("Duration:")
    lines.append(f"{c1['course_name']}: {c1['duration']}")
    lines.append(f"{c2['course_name']}: {c2['duration']}")
    lines.append("")
    lines.append("Mode:")
    lines.append(f"{c1['course_name']}: {c1['mode']}")
    lines.append(f"{c2['course_name']}: {c2['mode']}")
    lines.append("")
    lines.append("Seats:")
    lines.append(f"{c1['course_name']}: {c1['seats']}")
    lines.append(f"{c2['course_name']}: {c2['seats']}")

    lines.append("")
    lines.append("Placements:")
    lines.append(f"{c1['course_name']}: {c1['placements']}")
    lines.append(f"{c2['course_name']}: {c2['placements']}")

    return "\n".join(lines)


def handle_user_query(query: str):
    q = norm(query)

    if "compare" in q:
        q = q.replace("compare", "")

    if "vs" in q:
        a, b = q.split("vs", 1)
        return compare_courses_text(a.strip(), b.strip())

    return "Please ask a comparison using 'vs'."



def demo():
    tests = [
        "Compare btech in ai vs btech in aiml",
        # "compare MBA innovation vs mtech mechanical",
        # "B.Tech CSE vs B.Tech AI ML",
    ]

    for t in tests:
        print("Query:", t)
        print(handle_user_query(t))
        print("-" * 50)


if __name__ == "__main__":
    demo()
