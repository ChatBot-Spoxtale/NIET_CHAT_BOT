import requests
from bs4 import BeautifulSoup

URLS = {
    "infrastructure": "https://www.niet.co.in/campus-facilities/infrastructure",
    "hostel": "https://www.niet.co.in/campus-facilities/hostel"
}

def run():
    data = {}
    for k, url in URLS.items():
        soup = BeautifulSoup(requests.get(url).text,"lxml")
        title = soup.find("h1").text.strip()
        summary = next((p.text.strip() for p in soup.find_all("p") if len(p.text)>40),"")
        feats = [li.text.strip() for li in soup.find_all("li") if 6<len(li.text)<60][:10]
        data[k] = {
            "facility_name": title,
            "summary": summary,
            "features": feats,
            "source_url": url
        }
    return data
