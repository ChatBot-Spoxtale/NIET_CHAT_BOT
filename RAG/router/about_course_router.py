# RAG/routers/about_course_router.py

import json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

with open("RAG/data/about_course_chunks.json", "r", encoding="utf-8") as f:
    ABOUT_DATA = json.load(f)



PRIORITY_MAP = [
    ("master of computer applications", "mca"),
    ("mca", "mca"),
    
    ("master of business administration", "mba"),
    ("mba innovation", "mba"),
    ("mba marketing", "mba"),
    ("mba", "mba"),

    ("m.tech", "mtech"),
    ("mtech", "mtech"),

    ("btech cse aiml", "btech"),
    ("btech cse data science", "btech"),
    ("btech cse", "btech"),
    ("btech it", "btech"),
    ("btech ece", "btech"),
    ("btech mechanical", "btech"),
    ("btech", "btech"),
    
    ("twinning program", "international"),
    ("international twinning", "international"),
    
    ("bca", "bca"),
    ("bba", "bba"),
]

def about_course_router(query: str):
    q = query.lower().strip()
    
    replace_map = {
        "-": " ",
        ".": " ",
        "&": " and ",
        "(": " ",
        ")": " ",
    }
    for old, new in replace_map.items():
        q = q.replace(old, new)

    q = " ".join(q.split())


    TRIGGERS = ["tell me about", "why choose", "overview", "details", "info", "about"]
    if not any(t in q for t in TRIGGERS):
        return None

    for key, tag in PRIORITY_MAP:
        if key in q:
            for item in ABOUT_DATA:
                text = item["question"].lower()
                if tag in text:
                    return format_response(item)

    for item in ABOUT_DATA:
        if any(word in q for word in item["question"].lower().replace("tell me about ", "").split()):
            return format_response(item)

    return "Course not found in data. Please check the course name."



def format_response(item):
    return f"""

{item['answer']}

"""


if __name__ == "__main__":
    print(about_course_router("Tell me about B.Tech IT at NIET"))
    print(about_course_router("Tell me about B.Tech CSE (Artificial Intelligence and Machine Learning)"))
    print(about_course_router("Why choose Mechanical Engineering at NIET?"))
    print(about_course_router("Tell me about International Twinning Program"))
    print(about_course_router("Tell me about MBA"))

