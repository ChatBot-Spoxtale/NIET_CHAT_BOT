import json, os
from enrich_placements import parse_placement_page

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "placements.json")

def run_placements():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    placements = {}

    for url in urls.get("placements", []):
        try:
            data = parse_placement_page(url)
            if data:
                placements[url] = data
        except Exception as e:
            print(f"⚠️ Placement failed → {e}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(placements, f, indent=2, ensure_ascii=False)

    print("✅ placements.json generated")

if __name__ == "__main__":
    run_placements()
