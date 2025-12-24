# facilities.py
import json
import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

OUTPUT_PATH = "data/facilities.json"
HEADERS = {
    "User-Agent": "NIET-Chatbot-Scraper/1.0"
}

# -------------------------------------------------------------------
# URL SOURCE (AUTO – NO HARD CODING)
# -------------------------------------------------------------------

def load_facility_urls() -> Dict[str, List[str]]:
    with open("data/urls_meta.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_urls = data.get("facilities", [])

    categorized = {
        "academic_facilities": [],
        "hostel_facilities": [],
        "other_facilities": [],
        "sports_facilities": [],
        "medical_facilities": []
    }

    for url in raw_urls:
        u = url.lower()

        if "academic" in u:
            categorized["academic_facilities"].append(url)

        elif "hostel" in u:
            categorized["hostel_facilities"].append(url)

        elif "other" in u:
            categorized["other_facilities"].append(url)

        elif "sports" in u or "health" in u:
            categorized["sports_facilities"].append(url)

        elif "medical" in u:
            categorized["medical_facilities"].append(url)

    return categorized

# -------------------------------------------------------------------
# CORE SCRAPER
# -------------------------------------------------------------------

def clean_text(text: str) -> str:
    return " ".join(text.split())

def extract_facility_sections(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")

    main = soup.find("section", class_="main_content")
    if not main:
        return []

    sections = []

    for block in main.select(
        ".about-title, .activity-cont, .classroom-cont, "
        ".laborator-cont, .quality-cont"
    ):
        title_tag = block.find(["h4", "h3", "h2"])
        title = clean_text(title_tag.get_text()) if title_tag else None

        paragraphs = [
            clean_text(p.get_text())
            for p in block.find_all("p")
            if clean_text(p.get_text())
        ]

        if not paragraphs:
            continue

        sections.append({
            "title": title,
            "description": " ".join(paragraphs)
        })

    return sections

# -------------------------------------------------------------------
# SCRAPE SINGLE URL
# -------------------------------------------------------------------

def scrape_facility_page(url: str) -> List[Dict]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        sections = extract_facility_sections(r.text)

        for s in sections:
            s["url"] = url

        return sections

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return []

# -------------------------------------------------------------------
# MAIN RUNNER
# -------------------------------------------------------------------

def run():
    print("▶ Loading facility URLs...")
    facility_urls = load_facility_urls()

    final_data = {}

    for category, urls in facility_urls.items():
        print(f"▶ Scraping {category} ({len(urls)} URLs)")
        final_data[category] = []

        for url in urls:
            data = scrape_facility_page(url)
            final_data[category].extend(data)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✔ Facilities data saved to {OUTPUT_PATH}")

# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    run()
