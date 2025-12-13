import json
from pathlib import Path
from pdf_course_parser import extract_syllabus, extract_fees
from enrich_why_choose import extract_advantages
from enrich_facilities import run as extract_facilities

BASE = Path(__file__).resolve().parent
HTML = BASE / "data/incoming/html"
PDF = BASE / "data/incoming/pdf"
OUT = BASE / "data/base_knowledge.json"

kb = {"courses": {}, "facilities": {}}

for f in HTML.glob("*.json"):
    d = json.load(open(f))
    if d["type"] == "course":
        key = d["course_name"].lower().replace(" ", "_")
        kb["courses"][key] = d

for pdf in PDF.glob("*.pdf"):
    name = pdf.stem.lower()
    for c in kb["courses"].values():
        cname = c["course_name"].lower()
        if any(w in name for w in cname.split() if len(w)>3):
            syl = extract_syllabus(pdf)
            if syl: c["syllabus"] = syl
            fee = extract_fees(pdf)
            if fee: c["fees"] = fee

for c in kb["courses"].values():
    if not c["why_choose"]:
        adv = extract_advantages(c["course_name"])
        if adv:
            c["why_choose"] = {"source":"web","content":adv}

kb["facilities"] = extract_facilities()
json.dump(kb, open(OUT,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
print("✅ base_knowledge.json updated")
