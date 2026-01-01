# RAG/routers/placement_router.py
import json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from RAG.alias_map.alias_map import DEPT_ALIASES  

with open("RAG/data/placements_final_chunks.json","r",encoding="utf-8") as f:
    PLACEMENT_DATA = json.load(f)

def normalize(q: str):
    q = q.lower().strip()

    corrections = {
        "btech": "b.tech",
        "btch": "b.tech",

        # Mechanical Engineering
        " btech me": "mechanical",
        " b tech me": "mechanical",
        "mech engg": "mechanical engineering",
        "me engg": "mechanical engineering",
        "me ": "mechanical",   

        # CSBS
        "btech csbs": "csbs",
        "b tech csbs": "csbs",
        "tcs csbs": "csbs",

        # AIML
        "cse aiml": "aiml",
        "ai ml": "aiml",
        "ml": "aiml",

        # Data Science
        "cse ds": "data science",
        "btech ds": "data science",

        # IoT
        "btech iot": "internet of things",

        # Cyber
        "cse cy": "cyber security",
        "cy": "cyber security",
    }

    for wrong, right in corrections.items():
        q = q.replace(wrong, right)

    return q


PLACEMENT_KEYWORDS = {
    "mechanical": [
        "mechanical", "me", "btech me", "mechanical engineering", "mech", "me engg"
    ],
    "csbs": [
        "csbs", "btech csbs", "computer science and business systems"
    ],
    "cse": [
        "cse", "btech cse", "computer science", "software engineering"
    ],
    "aiml": [
        "aiml", "btech aiml", "ai ml", "cse aiml", "artificial intelligence"
    ],
    "data science": [
        "data science", "btech ds", "cse ds"
    ],
    "internet of things": [
        "iot", "internet of things", "btech iot"
    ],
    "cyber security": [
        "cyber security", "cse cy", "cyber"
    ],
    "mca": ["mca", "masters of computer application"],
    "mba": ["mba", "masters of business administration"]
}

def detect_department(q: str):
    q = normalize(q)
    for dept, aliases in PLACEMENT_DATA.items():
        for a in aliases:
            if a in q:
                return dept
    return None


def detect_metric(q: str):
    if "average" in q or "avg" in q:
        return "average"
    if "high" in q or "highest" in q or "max" in q:
        return "highest"
    if "how many" in q or "count" in q or "total" in q:
        return "placements"
    return None  


def placement_router(query: str):
    q = normalize(query)
    
    if not any(word in q for word in ["placement","package","lpa","average","highest","salary"]):
        return None

    dept = detect_department(q)
    metric = detect_metric(q)

    if not dept:
        return "Please specify department like: CSE, AIML, DS, IoT, CSBS, MCA, MBA, ME etc."

    results = []
    for item in PLACEMENT_DATA:
        text = normalize(item.get("question",""))
        ans = item.get("answer","")

        if dept in text: 
            if metric == "average" and "average" in text:
                return ans
            if metric == "highest" and "highest" in text:
                return ans
            if metric == "placements" and ("how many" in text or "recorded" in ans):
                return ans
            
            results.append(ans)

    if results:
        return f"{dept.upper()} Placement Details\n" + results[0]

    return f"No placement record found for {dept.upper()}in dataset."


if __name__ == "__main__":
    print(placement_router("average package of btech aiml"))
    print(placement_router("highest package in cse ai"))
    print(placement_router("how many placements in iot"))
