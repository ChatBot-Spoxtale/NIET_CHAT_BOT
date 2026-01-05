import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "research_data.json")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def get_research_urls():
    if not os.path.exists(URLS_FILE):
        raise FileNotFoundError("urls_meta.json not found. Run discover_urls.py first.")

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = {"overview": None, "areas": None, "patents": None, "projects": None}

    for url in data.get("research", []):
        if "overview" in url:
            urls["overview"] = url
        elif "areas-of-research" in url:
            urls["areas"] = url
        elif "patents" in url:
            urls["patents"] = url
        elif "research-project" in url:
            urls["projects"] = url

    return urls


def extract_overview(url):
    fallback_url = "https://www.niet.co.in/research"

    for target_url in [fallback_url, url]:
        if not target_url:
            continue

        r = requests.get(target_url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        container = soup.select_one("div.niet-institute.stu-walfr")
        if not container:
            continue

        summary = ""
        summary_p = container.select_one(
            "div.col-lg-4 div.stu.niet-img.list-itm > p"
        )
        if summary_p:
            summary = clean(summary_p.get_text())

        highlights = []
        highlights_ul = container.select_one(
            "div.col-lg-8 div.niet-img.live-pr-img ul"
        )
        if highlights_ul:
            highlights = [
                clean(li.get_text())
                for li in highlights_ul.find_all("li")
            ]

        if summary or highlights:
            return {
                "summary": summary,
                "highlights": highlights
            }

    return {}

def extract_areas(url):
    if not url:
        return []

    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    return [clean(li.get_text()) for li in soup.select(".benefits_listing li span")]


def extract_patents(url):
    if not url:
        return {}

    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    data = {}
    for box in soup.select(".lpa_counter"):
        label = box.find("h4").get_text(strip=True).lower()
        value = int(box.find("h3").get_text(strip=True))

        if "design" in label and "published" in label:
            data["design_published"] = value
        elif "design" in label and "granted" in label:
            data["design_granted"] = value
        elif "standard" in label and "published" in label:
            data["standard_published"] = value
        elif "standard" in label and "granted" in label:
            data["standard_granted"] = value

    return data

def extract_projects(url):
    if not url:
        return []

    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    projects = []
    for row in soup.select(".fee-stru table tbody tr"):
        cols = [clean(td.get_text()) for td in row.find_all("td")]
        if len(cols) >= 5:
            projects.append({
                "department": cols[1],
                "faculty": cols[2],
                "grant": cols[3],
                "year": cols[4]
            })

    return projects

def run_research_scraper():
    print("🔬 Scraping research data")

    urls = get_research_urls()

    data = {
        "overview": extract_overview(urls["overview"]),
        "areas_of_research": extract_areas(urls["areas"]),
        "patents": extract_patents(urls["patents"]),
        "research_projects": extract_projects(urls["projects"])
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ research_data.json generated")


if __name__ == "__main__":
    run_research_scraper()
