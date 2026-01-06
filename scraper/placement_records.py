import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "placement_records.json")

HEADERS = {
    "User-Agent": "NIET-Chatbot-Scraper/1.0"
}

def extract_carousel_images(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    images = set()

    for img in soup.select(".record_box img"):
        src = img.get("src")
        if src:
            images.add(urljoin(url, src))

    return sorted(images)

def run():
    if not os.path.exists(URLS_FILE):
        raise FileNotFoundError("urls_meta.json not found. Run discover_urls.py first.")

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls_meta = json.load(f)

    urls = urls_meta.get("placement_records", [])

    if not urls:
        print("⚠️ No placement records URL found")
        return

    all_images = []

    for url in urls:
        print(f"▶ Scraping placement records from {url}")
        images = extract_carousel_images(url)
        all_images.extend(images)

    data = {
        "placement_record_images": all_images,
        "source_url": urls
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ placement_records.json generated ({len(all_images)} images)")

if __name__ == "__main__":
    run()
