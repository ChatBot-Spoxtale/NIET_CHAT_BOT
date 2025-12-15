import requests
from bs4 import BeautifulSoup

def parse_placement_page(url):
    data = {}
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for box in soup.select(".lpa_counter"):
            value = box.find("h3").get_text(strip=True)
            label = box.find("h4").get_text(strip=True).lower()

            if "highest" in label:
                data["highest_package"] = value
            elif "average" in label:
                data["average_package"] = value
            elif "placement" in label:
                data["placements_offered"] = value
    except:
        pass

    return data
