import requests, re

def extract_meta(course_url):
    meta = {"duration": "", "seats": ""}
    try:
        text = requests.get(course_url, timeout=10).text
        plain = re.sub("<[^>]+>", " ", text)

        d = re.search(r"Duration\s*[:\-]?\s*(\d+\s*Years?)", plain, re.I)
        if d:
            meta["duration"] = d.group(1)

        s = re.search(r"(Seats|Intake)\s*[:\-]?\s*(\d+)", plain, re.I)
        if s:
            meta["seats"] = s.group(2)
    except:
        pass

    return meta
