import json, os
from enrich_facilities import extract_facilities

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "facilities.json")

def run_facilities():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    facilities = extract_facilities(urls.get("facilities", []))

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(facilities, f, indent=2, ensure_ascii=False)

    print("✅ facilities.json generated")

if __name__ == "__main__":
    run_facilities()
