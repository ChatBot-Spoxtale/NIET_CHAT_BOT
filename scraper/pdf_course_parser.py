import re, pdfplumber

def extract_syllabus(pdf):
    out = []
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            for line in (page.extract_text() or "").split("\n"):
                if re.search(r"(semester|sem)\s*[ivx\d]+", line, re.I):
                    if 10 < len(line) < 120:
                        out.append(line.strip())
    return list(dict.fromkeys(out))[:12]

def extract_fees(pdf):
    with pdfplumber.open(pdf) as p:
        text = " ".join(pg.extract_text() or "" for pg in p.pages)
    m = re.search(r"₹\s?[\d,]+", text)
    return m.group(0) if m else ""
