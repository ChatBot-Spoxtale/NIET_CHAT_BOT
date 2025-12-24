import json
from pathlib import Path

# ---------------- PATHS ----------------
BASE = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE / "data" / "placement.json"
INDEX_STORE = BASE / "index_store"
OUTPUT_FILE = INDEX_STORE / "placement_chunks.json"

INDEX_STORE.mkdir(exist_ok=True)

# ---------------- HELPERS ----------------
def extract_department(url: str) -> str:
    slug = url.rstrip("/").split("/")[-2]
    slug = slug.replace("-", " ")
    return slug.title()

def make_id(dept: str, metric: str) -> str:
    return f"{dept.lower().replace(' ', '_')}_{metric}"

# ---------------- MAIN CHUNK FUNCTION ----------------
def build_placement_chunks(input_path: Path, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []

    for url, info in data.items():
        department = extract_department(url)

        if "placements_offered" in info:
            chunks.append({
                "id": make_id(department, "placements"),
                "category": "placement",
                "department": department,
                "metric": "placements_offered",
                "value": info["placements_offered"],
                "url": url,
                "text": f"The {department} department recorded {info['placements_offered']} placements."
            })

        if "highest_package" in info:
            chunks.append({
                "id": make_id(department, "highest_package"),
                "category": "placement",
                "department": department,
                "metric": "highest_package",
                "value": info["highest_package"],
                "url": url,
                "text": f"The highest package offered in the {department} department was {info['highest_package']}."
            })

        if "average_package" in info:
            chunks.append({
                "id": make_id(department, "average_package"),
                "category": "placement",
                "department": department,
                "metric": "average_package",
                "value": info["average_package"],
                "url": url,
                "text": f"The average package in the {department} department was {info['average_package']}."
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Placement chunks created: {len(chunks)}")
    print(f"Saved at: {output_path}")

# ---------------- RUN ----------------
if __name__ == "__main__":
    build_placement_chunks(INPUT_FILE, OUTPUT_FILE)
