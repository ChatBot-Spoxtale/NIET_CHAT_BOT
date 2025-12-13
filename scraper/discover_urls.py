import requests, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

ROOT = "https://www.niet.co.in"
BASE = Path(__file__).resolve().parent / "data"
OUT = BASE / "urls_meta.json"

def collect(url):
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = href if href.startswith("http") else urljoin(ROOT, href)

        if full.startswith(ROOT) and (
            "/course/" in full or
            "/campus-facilities/infrastructure" in full or
            "/campus-facilities/hostel" in full or
            full.endswith(".pdf")
        ):
            urls.add(full.split("#")[0])

    return urls

urls = set()
for p in ["/courses", "/placements", "/campus-facilities"]:
    urls |= collect(ROOT + p)

BASE.mkdir(exist_ok=True)
json.dump({"urls": sorted(urls)}, open(OUT, "w"), indent=2)
print("URLs discovered:", len(urls))
