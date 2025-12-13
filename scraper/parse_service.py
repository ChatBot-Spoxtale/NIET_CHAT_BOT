from flask import Flask, request, jsonify
import requests, json, hashlib, re, subprocess
from bs4 import BeautifulSoup
from pathlib import Path

app = Flask(__name__)

BASE = Path(__file__).resolve().parent
HTML = BASE / "data" / "incoming" / "html"
PDF = BASE / "data" / "incoming" / "pdf"
HTML.mkdir(parents=True, exist_ok=True)
PDF.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "NIET-Scraper"}

def sha(x): return hashlib.sha256(x.encode()).hexdigest()
def clean(t): return re.sub(r"\s+", " ", t).strip()

def detect(url):
    u = url.lower()
    if u.endswith(".pdf"): return "pdf"
    if "/course/" in u: return "course"
    if "campus-facilities" in u: return "facility"
    return "ignore"

def extract_course(soup, url):
    text = soup.get_text(" ")

    name = clean(soup.find("h1").text) if soup.find("h1") else ""
    dur = re.search(r"\d+\s*(year|years)", text, re.I)
    duration = dur.group(0) if dur else ""

    seats = ""
    for tag in soup.find_all(["p","div","span","li"]):
        t = clean(tag.get_text(" "))
        if any(k in t.lower() for k in ["intake","seats"]):
            m = re.search(r"\b\d{2,3}\b", t)
            if m:
                seats = m.group()
                break

    return {
        "type": "course",
        "course_name": name,
        "duration": duration,
        "mode": "Full Time",
        "seats": seats,
        "why_choose": "",
        "source_url": url
    }

def extract_facility(soup, url):
    title = clean(soup.find("h1").text)
    summary = next((clean(p.text) for p in soup.find_all("p") if len(p.text) > 40), "")
    feats = [clean(li.text) for li in soup.find_all("li") if 6 < len(li.text) < 60][:10]

    return {
        "type": "facility",
        "facility_name": title,
        "summary": summary,
        "features": feats,
        "source_url": url
    }

@app.route("/parse", methods=["POST"])
def parse():
    url = request.json["url"]
    kind = detect(url)

    if kind == "ignore":
        return jsonify({"ignored": url})

    if kind == "pdf":
        r = requests.get(url, headers=HEADERS)
        open(PDF / url.split("/")[-1], "wb").write(r.content)
    else:
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        data = extract_course(soup, url) if kind=="course" else extract_facility(soup, url)
        json.dump(data, open(HTML / f"{sha(url)}.json","w",encoding="utf-8"), indent=2)

    subprocess.Popen(["python", "build_base_knowledge.py"])
    return jsonify({"parsed": url})

if __name__ == "__main__":
    app.run(port=5001)
