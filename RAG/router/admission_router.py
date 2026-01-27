import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path to club data JSON
DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data_chunk",
    "admission_data_chunk",
    "admission_chunks.json"
)
with open(DATA_PATH, "r", encoding="utf-8") as f:
    ADMISSION_DATA = json.load(f)


def clean_text(text: str):
    """Normalize input for better matching"""
    replace_map = {
        "-": " ",
        ".": " ",
        "&": " and ",
        "(": " ",
        ")": " ",
        ",": " ",
    }
    text = text.lower()
    for old, new in replace_map.items():
        text = text.replace(old, new)
    return " ".join(text.split())


PRIORITY_MAP = [
    ("btech it", "btech it"),
    ("b tech it", "btech it"),
    ("information technology", "btech it"),

    ("btech cse", "btech cse"),
    ("computer science engineering", "btech cse"),

    ("btech", "first year  btech"),   

    ("mca", "first year  mca"),
    ("master of computer applications", "first year  mca"),

    ("mba", "first year  mba"),
    ("business administration", "first year  mba"),

    ("lateral entry btech", "lateral entry btech"),
    ("lateral entry", "lateral entry btech"),

    ("b.pharm", "first year  b.pharm"),
    ("pharmacy", "first year  b.pharm"),

    ("pgdm", "for admission to pgdm course"),
    ("m.tech", "for admission to m.tech course"),
    ("mtech", "for admission to m.tech course"),

    ("twinning", "twinning_program"),
]
import re

def remove_urls(text: str):
    return re.sub(r'https?://\S+|www\.\S+', '', text)


def normalize_answer(text: str):
    text = remove_urls(text)         
    text = text.replace("•", "")
    text = text.replace("  ", " ")
    return text.strip()


def collect_admission_data():
    sections = {
        "process": [],
        "eligibility": [],
        "registration": [],
        "other": []
    }

    for row in ADMISSION_DATA:
        raw_answer = row.get("answer", "")

        answer = normalize_answer(raw_answer)
        answer = clean_text(answer)

        course = clean_text(row.get("course", ""))
        answer_lower = answer.lower()

        if "admission process" in answer_lower or "allotment" in answer_lower:
            sections["process"].append(answer)

        elif "documents required" in answer_lower or "mark sheet" in answer_lower:
            sections["eligibility"].append(answer)

        elif "registration" in answer_lower or "apply" in answer_lower:
            sections["registration"].append(answer)

        elif "first year" in course or "lateral" in course:
            sections["eligibility"].append(answer)

        else:
            sections["other"].append(answer)

    return sections

def get_unique_courses():
    courses = set()

    for row in ADMISSION_DATA:
        course = row.get("course", "").strip()
        if course and course.lower() not in ["admission", "direct", "jee_main"]:
            courses.add(course)

    return sorted(courses)
def group_admission_by_course():
    grouped = {}

    for row in ADMISSION_DATA:
        course = row.get("course", "").strip()
        answer = normalize_answer(row.get("answer", "")).strip()

        if not course or course.lower() in ["admission", "direct", "jee_main"]:
            continue

        if course not in grouped:
            grouped[course] = []

        grouped[course].append(answer)

    return grouped

def format_all_courses_admission():
    grouped = {}

    for row in ADMISSION_DATA:
        course = row.get("course", "").strip()
        answer = normalize_answer(row.get("answer", "")).strip()

        if not course:
            continue

        if course not in grouped:
            grouped[course] = []

        grouped[course].append(answer)

    response = []
    response.append("🎓 Admission Process – NIET (All Courses)\n")

    for course, answers in grouped.items():
        response.append(f"📌 {course}")
        for ans in answers:
            parts = re.split(r";|\.\s+", ans)
            for p in parts:
                if p.strip():
                    response.append(f"• {p.strip()}")
        response.append("")

    response.append("🔗 Official Details:")
    response.append("https://www.niet.co.in/admissions/eligibility-admission-process")
    response.append("\n🔗 For Registration:")
    response.append("https://applynow.niet.co.in/")

    return "\n".join(response)



def admission_router(query: str):
    q = clean_text(query)

    for key, tag in PRIORITY_MAP:
        if key in q:
            for row in ADMISSION_DATA:
                course_clean = clean_text(row.get("course", ""))
                if tag in course_clean:
                    return format_admission(row)

    if "btech" in q or "b tech" in q:
        for row in ADMISSION_DATA:
            course_clean = clean_text(row.get("course", ""))
            if "first year btech" in course_clean:
                return format_admission(row)

    GENERIC_KEYWORDS = [
        "admission", "apply", "documents",
        "fees", "counselling", "eligibility", "registration"
    ]

    if any(k in q for k in GENERIC_KEYWORDS):
        return format_all_courses_admission()

    return group_admission_by_course()

def format_admission(row):
    response = []
    response.append(f"🎓 Admission Process – {row['course']}")

    answer = normalize_answer(row["answer"])
    parts = re.split(r";|\.\s+", answer)

    for p in parts:
        p = p.strip()
        if p:
            response.append(f"- {p}")

    response.append("\n🔗 Official details:")
    response.append("- https://www.niet.co.in/admissions/eligibility-admission-process")

    return "\n".join(response)



if __name__ == "__main__":
    print(admission_router("Admission Prcoess At NIET"))
    # print(admission_router("admission process for btech cse aiml"))
    print(admission_router("how to take admission in MCA"))
    # print(admission_router("b.tech cse admission process"))
    # print(admission_router("how to take admission in PGDM"))


