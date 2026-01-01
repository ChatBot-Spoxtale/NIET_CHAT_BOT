import json, os, re

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/ug_pg_router.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    UGPG_DATA = json.load(f)

def normalize(q: str):
    q = q.lower()
    q = re.sub(r"[^\w\s]", " ", q)
    return " ".join(q.split())

EMPTY_FIELD_WORDS = ["seat","seats","duration","year","years","time","timing"]
COURSE_HINTS = ["mba","mca","bca","bba","integrated"]

def ug_pg_router(query: str):
    q = normalize(query)

    if any(w in q for w in EMPTY_FIELD_WORDS) and not any(c in q for c in COURSE_HINTS):
        return "Please type full course name. Example:\nMBA duration\nBCA seats\nMCA placement record"

    for data in UGPG_DATA:
        if any(k in q for k in data.get("keywords", [])):

            if any(w in q for w in ["placement","package","salary","highest","average"]):
                plc = data.get("placements", {})
                return f"""Placement - {data['course']}
• Average Package: {plc.get('average','NA')}
• Highest Package: {plc.get('highest','NA')}
• Source: {plc.get('source_url','NA')}"""

            if any(w in q for w in ["overview","about","details","information"]):
                return f"""{data['course']} - Overview
{data.get('overview','No overview found.')}"""

            # Seats & Duration
            if "seat" in q or "duration" in q:
                p = data.get("properties", {})
                return f"""{data['course']}
• Seats: {p.get('seats','NA')}
• Duration: {p.get('duration','NA')}"""

            
            if any(w in q for w in ["eligibility","criteria","qualification","required","requirement"]):
                p = data.get("properties", {})
                return f"""Eligibility - {data['course']}**
         {p.get('eligibility','Not available')}"""
            
            if "why" in q or "benefit" in q or "choose" in q:
                reasons = "\n- ".join(data.get("why_choose", []))
                return f"Why Choose {data['course']}?\n- {reasons}"

            return f" {data['course']} identified.\nAsk something like:\n overview / placement / seats / duration / fees"

    return None  
