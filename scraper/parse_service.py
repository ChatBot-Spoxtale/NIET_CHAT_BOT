from flask import Flask, jsonify, request
import json, os, threading, time

from discover_urls import discover_urls
from enrich_why_choose import enrich_why_choose
from enrich_placements import parse_placement_page
from enrich_facilities import extract_facilities
from pdf_course_parser import extract_syllabus
from build_base_knowledge import extract_meta

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_FILE = os.path.join(DATA_DIR, "base_knowledge.json")


def run_scraping():
    print("\n🔄 SCRAPING STARTED")
    start = time.time()

    urls = discover_urls()

    courses = {}
    total = len(urls["courses"])

    for i, url in enumerate(urls["courses"], start=1):
        slug = url.rstrip("/").split("/")[-1]
        print(f"📘 [{i}/{total}] Processing course → {slug}")

        try:
            meta = extract_meta(url)
            syllabus = extract_syllabus(url)

            courses[slug] = {
                "course_name": slug.replace("-", " ").title(),
                "duration": meta.get("duration"),
                "seats": meta.get("seats"),
                "mode": "Full Time",
                "why_choose": enrich_why_choose({"source_url": url}),
                "syllabus": syllabus,   # PDF links only
                "placements": {},
                "source_url": url
            }
        except Exception as e:
            print(f"⚠️ Course failed: {slug} → {e}")

    print("🏢 Parsing placement pages")

    for purl in urls["placements"]:
        print(f"📊 Placement page → {purl}")
        pdata = parse_placement_page(purl)
        if pdata:
            for c in courses.values():
                c["placements"] = pdata

    print("🏫 Extracting facilities")
    facilities = extract_facilities(urls["facilities"])

    base = {
        "courses": courses,
        "facilities": facilities
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=2, ensure_ascii=False)

    print(f"✅ base_knowledge.json generated in {round(time.time()-start,2)}s\n")


@app.route("/parse", methods=["POST"])
def parse():
    print("🚀 PARSE TRIGGER RECEIVED")

    data = request.get_json(force=True, silent=True) or {}
    if not data.get("refresh"):
        print("⚠️ Ignored (no refresh flag)")
        return jsonify({"status": "ignored"})

    threading.Thread(target=run_scraping, daemon=True).start()

    return jsonify({
        "status": "started",
        "message": "Scraping running in background"
    })


if __name__ == "__main__":
    app.run(port=5001)
