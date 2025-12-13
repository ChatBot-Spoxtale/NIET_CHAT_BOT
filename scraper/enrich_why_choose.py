import requests
from bs4 import BeautifulSoup

def extract_advantages(course):
    q = f"Why choose {course} course advantages"
    url = f"https://www.google.com/search?q={q.replace(' ','+')}"
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "lxml")

    pts = []
    for p in soup.find_all("p"):
        t = " ".join(p.text.split())
        if any(k in t.lower() for k in ["career","skills","industry","scope"]) and 30 < len(t) < 200:
            pts.append(t)
        if len(pts) == 4:
            break
    return pts
