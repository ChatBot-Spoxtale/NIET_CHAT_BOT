# btech_router.py

import json, os, re

MTECH_PATH = os.path.join(os.path.dirname(__file__), "../data/mtech_chunks.json")
with open(MTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

MTECH_DATA = data if isinstance(data, list) else [data]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[.\-]', ' ', text)  
    return " ".join(text.split())


def mtech_router(query: str):
    q = normalize(query)

    if not any(word in q for word in [
    "mtech", "m tech", "m.tech",
    "master of technology", "master in technology",
    "integrated mtech", "master of integrated technology",
    "integrated technology"
]):
        return None


    for course in MTECH_DATA:

            if any(q == k for k in course["keywords"]):
                matched = True
            elif any(k in q for k in course["keywords"]):
                matched = True
            else:
                matched = False

            if not matched:
                continue

            if "seat" in q or "seats" in q:
                return f"Seats:{course['properties'].get('seats', 'Not available')}"

            if "duration" in q or "year" in q:
                return f"Duration:{course['properties'].get('duration', 'Not available')}"

            if "eligibility" in q or "criteria" in q:
                return f"Eligibility: {course['properties'].get('eligibility', 'Not available')}"

            if "fee" in q or "fees" in q:
                return f"Fees: {course['properties'].get('fees','Check admission department')}"

            if "placement" in q or "package" in q:
                p = course.get("placements", {})
                return f"""
• Average: {p.get('average','NA')}
• Highest: {p.get('highest','NA')}
• Url_Source: {p.get('source_url',"NA")}
""".strip()
            
            if any(w in q for w in ["eligibility","criteria","qualification","required","requirement"]):
                p = data.get("properties", {})
                return f"""Eligibility - {data['course']}**
• {p.get('eligibility','Not available')}"""
            
            if any(word in q for word in ["why choose","why this","benefit","advantage","kyu","kyun","kyo"]):
                why = course.get("why_choose", [])
                if why:
                    return "Why Choose this Course :-\n- " + "\n- ".join(why)
                else:
                    return "This course offers strong learning, placement, and future career scope."

            if any(word in q for word in ["overview","about","detail","tell me","kaisa","kya hai"]):
                return course.get("overview", "No overview available.")



def test_mtech_router():
    test_queries = [
        # "about btech aiml",
        " Overview Master of Integrated Technology in Computer Science and Engineering",
        # "btech cse aiml placement",
        # "what is the duration of btech cse aiml",
        # "what is the duration of btech cse ai",
        # "placement record of btech cse ds",
        # "why choose this btech cse ai"
    ]

    for q in test_queries:
        print(f"Query: {q}")
        print(f"Response: {mtech_router(q)}\n")


if __name__ == "__main__":
    test_mtech_router()
