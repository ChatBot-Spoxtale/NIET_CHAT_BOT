import json, os
from course_utils import extract_meta
from enrich_why_choose import enrich_why_choose

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "courses.json")

def run_courses():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    courses = {}

    for url in urls.get("courses", []):
        slug = url.rstrip("/").split("/")[-1]

        try:
            meta = extract_meta(url)

            courses[slug] = {
                "course_name": slug.replace("-", " ").title(),
                "duration": meta.get("duration"),
                "seats": meta.get("seats"),
                "mode": "Full Time",
                "why_choose": enrich_why_choose({"source_url": url}),
                "source_url": url
            }

        except Exception as e:
            print(f"⚠️ Course failed: {slug} → {e}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print("✅ courses.json generated")

if __name__ == "__main__":
    run_courses()
