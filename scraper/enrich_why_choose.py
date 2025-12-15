import requests
from bs4 import BeautifulSoup

def enrich_why_choose(course):
    try:
        r = requests.get(course["source_url"], timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        ul = soup.select_one(".prom-speci .progm-list ul")
        if not ul:
            return []

        return [li.get_text(strip=True) for li in ul.find_all("li")][:4]
    except:
        return []
