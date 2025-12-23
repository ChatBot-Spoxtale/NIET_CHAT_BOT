import json, os, re, requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

URLS_FILE = os.path.join(DATA_DIR, "urls_meta.json")
OUT_FILE = os.path.join(DATA_DIR, "about_courses.json")


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize_text(text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    summary = []
    for s in sentences:
        s = s.strip()
        if len(s) > 40:      
            summary.append(s)
        if len(summary) == max_sentences:
            break

    return " ".join(summary)


def extract_about_course(url):
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        about_div = soup.select_one(
            ".cretera-cous.course-cont.first"
        )

        if not about_div:
            return ""

        paragraphs = about_div.find_all("p")
        full_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

        return clean_text(full_text)

    except Exception as e:
        print(f"⚠️ About course extraction failed: {url} → {e}")
        return ""


def run_about_courses():
    if not os.path.exists(URLS_FILE):
        raise FileNotFoundError("urls_meta.json not found. Run discover_urls.py first.")

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    about_courses = {}

    for url in urls.get("courses", []):
        slug = url.rstrip("/").split("/")[-1]

        raw_text = extract_about_course(url)
        if not raw_text:
            continue

        about_courses[slug] = {
            "summary": summarize_text(raw_text)
        }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(about_courses, f, indent=2, ensure_ascii=False)

    print("✅ about_courses.json generated")


if __name__ == "__main__":
    run_about_courses()
