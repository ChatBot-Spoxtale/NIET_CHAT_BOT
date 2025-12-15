import requests
from bs4 import BeautifulSoup

def extract_facilities(urls):
    facilities = []

    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            section = soup.select_one(".main_content, .content, .inner-content")
            if section:
                facilities.append(section.get_text(" ", strip=True))

        except:
            pass

    return facilities
