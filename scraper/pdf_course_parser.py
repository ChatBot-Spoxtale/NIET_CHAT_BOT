import requests
from bs4 import BeautifulSoup

def extract_syllabus(course_url):
    try:
        r = requests.get(course_url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        pdfs = []
        for a in soup.select("a[href$='.pdf']"):
            href = a["href"]
            if "syllabus" in href.lower():
                pdfs.append(href)

        return pdfs

    except Exception as e:
        print("❌ syllabus error:", e)
        return []
