import os
import json
import requests
from bs4 import BeautifulSoup
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "institute_data.json")


def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def get_institute_urls():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = {
        "about": None,
        "awards": None,
        "rankings": None,
        "alliances": None
    }

    for url in data.get("institute", []):
        u = url.lower()
        if "overview" in u:
            urls["about"] = url
        elif "award" in u:
            urls["awards"] = url
        elif "ranking" in u:
            urls["rankings"] = url
        elif "international" in u:
            urls["alliances"] = url

    return urls

def extract_about(url):
    if not url:
        return {}

    soup = BeautifulSoup(requests.get(url, timeout=15).text, "html.parser")

    text_block = soup.select_one(".news.new-one p")
    summary = clean(text_block.get_text()) if text_block else ""

    highlights = []
    for box in soup.select(".why-brnd-logo .logo-item p"):
        highlights.append(clean(box.get_text()))

    return {
        "summary": summary,
        "highlights": highlights
    }

def extract_awards(url):
    if not url:
        return []

    soup = BeautifulSoup(requests.get(url, timeout=15).text, "html.parser")

    awards = []
    for card in soup.select(".teaching-list"):
        p = card.select_one("p")
        img = card.select_one("img")

        if p:
            awards.append({
                "title": clean(p.get_text()),
                "image": img["src"] if img else None
            })

    return awards

def extract_rankings(url):
    if not url:
        return []

    soup = BeautifulSoup(requests.get(url, timeout=15).text, "html.parser")

    rankings = []
    for block in soup.select(".ranking-wrapper"):
        heading = block.select_one("h6")
        for item in block.select(".online-content p"):
            rankings.append({
                "category": clean(heading.get_text()) if heading else "",
                "detail": clean(item.get_text())
            })

    return rankings

def extract_alliances(url):
    if not url:
        return []

    soup = BeautifulSoup(requests.get(url, timeout=15).text, "html.parser")

    alliances = []
    for img in soup.select(".gallery-grp img"):
        alliances.append(img["src"])

    return alliances

def run_institute_scraper():
    print("Scraping institute data")

    urls = get_institute_urls()

    data = {
        "about_institute": extract_about(urls["about"]),
        "awards_and_accolades": extract_awards(urls["awards"]),
        "rankings_and_ratings": extract_rankings(urls["rankings"]),
        "international_alliances": extract_alliances(urls["alliances"])
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("institute_data.json generated")


if __name__ == "__main__":
    run_institute_scraper()
