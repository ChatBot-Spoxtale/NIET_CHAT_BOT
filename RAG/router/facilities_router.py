import json
import os
import re

from llm_model_gemini.llm.gemini_client import generate_answer
# Project root (RAG/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data_chunk",
    "facilities_data_chunk",
    "facility_chunks.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    FACILITY_DATA = json.load(f)


def to_bullets(text: str):
    """
    Convert paragraphs into bullet points
    """
    lines = re.split(r"\n+|\. ", text)
    bullets = []
    for line in lines:
        line = line.strip()
        if len(line) > 10:
            bullets.append(f"• {line}")
    return bullets


def extract_url(text: str):
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def facility_router(query: str):
    q = query.lower()

    academic_points = []
    hostel_points = []
    academic_url = None
    hostel_url = None

    for item in FACILITY_DATA:
        if not isinstance(item, dict):
            continue

        category = item.get("category")
        answer = item.get("answer", "")

        if not answer:
            continue

        bullets = to_bullets(answer)
        url = extract_url(answer)

        if category == "campus_facilities":
            academic_points.extend(bullets)
            if url:
                academic_url = url

        if category == "hostel_facilities":
            hostel_points.extend(bullets)
            if url:
                hostel_url = url
    academic_url="https://niet.co.in/infrastructure/academic-facilities"
    # Academic only
    if "academic" in q:
        return (
            "Academic Facilities at NIET\n\n"
            + "\n".join(academic_points)
            + (f"\n\n🔗 {academic_url}" if academic_url else "")
        )
    hostel_url="https://niet.co.in/campus-facilities/about-hostel"
    # Hostel only
    if "hostel" in q:
        return (
            "Hostel Facilities at NIET\n\n"
            + "\n".join(hostel_points)
            + (f"\n\n🔗 {hostel_url}" if hostel_url else "")
        )

    # Both
    if "facility" in q or "facilities" in q:
        return (
            "🏫 Academic Facilities at NIET\n\n"
            + "\n".join(academic_points)
            + (f"\n\n🔗 {academic_url}" if academic_url else "")
            + "\n\n"
            + "🏠 Hostel Facilities at NIET\n\n"
            + "\n".join(hostel_points)
            + (f"\n\n🔗 {hostel_url}" if hostel_url else "")
        )

    return None

# ---- Local test ----
if __name__ == "__main__":
    print(facility_router("Academic Facilities"))
    print("-" * 50)
    print(facility_router("Hostel Facilities"))
