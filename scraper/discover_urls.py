import requests, json, os
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_FILE = os.path.join(DATA_DIR, "urls_meta.json")

SITEMAP = "https://www.niet.co.in/sitemap.xml"

def discover_urls():
    os.makedirs(DATA_DIR, exist_ok=True)

    r = requests.get(SITEMAP, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    data = {
        "courses": [],
        "placements": [],
        "facilities": [],
        "research": [],
        "institute": [],
        "pdfs": []
    }

    for url in root.findall("ns:url", ns):
        loc = url.find("ns:loc", ns).text.strip()

        if "/course/" in loc:
            data["courses"].append(loc)
        elif "/department/" in loc and loc.endswith("/placement"):
            data["placements"].append(loc)
        elif any(x in loc for x in ["/campus-facilities", "/infrastructure"]):
            data["facilities"].append(loc)
        elif "/research/" in loc:
            data["research"].append(loc)
        elif "/why-us/" in loc:
            data["institute"].append(loc)
        elif loc.lower().endswith(".pdf"):
            data["pdfs"].append(loc)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✔ URL discovery done")
    for k, v in data.items():
        print(f"{k}: {len(v)}")

    return data

if __name__ == "__main__":
    discover_urls()