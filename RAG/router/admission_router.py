import json
import os
import re

# ---------- Load Data ----------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data_chunk",
    "admission_data_chunk",
    "admission_chunks.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    ADMISSION_DATA = json.load(f)


# ---------- Helpers ----------
def clean_text(text: str) -> str:
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


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def normalize_answer(text: str) -> str:
    text = remove_urls(text or "")
    text = text.replace("•", "")
    return " ".join(text.split()).strip()


# ---------- Format Single Admission ----------
def format_admission(row: dict) -> str:
    response = []

    # ✅ Use QUESTION (not course – course does not exist in JSON)
    title = row.get("question", "Admission Details")
    response.append(f"🎓 {title}")

    answer = normalize_answer(row.get("answer", ""))
    parts = re.split(r";|\.\s+", answer)

    for p in parts:
        if p.strip():
            response.append(f"- {p.strip()}")

    response.append("\n🔗 Official details:")
    response.append("- https://www.niet.co.in/admissions/eligibility-admission-process")

    return "\n".join(response)


# ---------- Format Full Admission ----------
def format_all_courses_admission() -> str:
    response = []
    response.append("🎓 Admission Process – NIET (All Courses)\n")

    for row in ADMISSION_DATA:
        title = row.get("question", "Admission Details")
        response.append(f"📌 {title}")

        answer = normalize_answer(row.get("answer", ""))
        parts = re.split(r";|\.\s+", answer)
        for p in parts:
            if p.strip():
                response.append(f"• {p.strip()}")

        response.append("")

    response.append("🔗 Official Details:")
    response.append("https://www.niet.co.in/admissions/eligibility-admission-process")
    response.append("\n🔗 For Registration:")
    response.append("https://applynow.niet.co.in/")

    return "\n".join(response)


# ---------- Keyword Matching ----------
def keyword_match(query: str, keywords: list) -> bool:
    """Return True if at least 2 keywords match"""
    score = 0
    for kw in keywords:
        if kw.lower() in query:
            score += 1
    return score >= 2


def admission_router(query: str) -> str:
    q = clean_text(query)

    if any(k in q for k in [
        "admission process",
        "how to take admission",
        "admission details",
        "admission at niet"
    ]):
        return format_all_courses_admission()

    matched = []
    for row in ADMISSION_DATA:
        if keyword_match(q, row.get("keywords", [])):
            matched.append(row)

    if matched:
        return "\n\n".join(format_admission(r) for r in matched)

    if any(k in q for k in [
        "admission", "apply", "documents",
        "fees", "counselling", "eligibility", "registration"
    ]):
        return format_all_courses_admission()

    return format_all_courses_admission()


if __name__ == "__main__":
    print(admission_router("Admission Process At NIET"))
    print("\n" + "="*60 + "\n")
    print(admission_router("eligibility for first year btech"))
    print("\n" + "="*60 + "\n")
    print(admission_router("mca admission eligibility"))