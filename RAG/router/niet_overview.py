# RAG/routers/about_niet_router.py
import json, os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from Ollama.llm_client import ask_ollama_with_context

with open("RAG/data/combined_chunks.json","r",encoding="utf-8") as f:
    NIET_DATA = json.load(f)


def normalize(q: str):
    q = q.lower().strip()
    fixes = {
        "niett": "niet",
        "net": "niet",
        "neet": "niet",
        "addmission": "admission",
        "infra": "infrastructure",
        "campous": "campus",
    }
    for wrong, right in fixes.items():
        q = q.replace(wrong, right)
    return q


ABOUT_TRIGGERS = [
    "about niet", "what is niet", "why niet", "know niet",
    "niet info", "niet overview", "niet details", "niet description",
    "why choose niet"
]


def about_niet_router(query: str):
    q = normalize(query)

    if not any(trigger in q for trigger in ABOUT_TRIGGERS):
        return None

    for item in NIET_DATA:
        question = normalize(item.get("question",""))
        ans = item.get("answer","")

        if any(word in question for word in q.split()):
            return f"""
About NIET
{ans}

Need more:-
• Courses Offered
• Admission Process
• Placement Record
• Hostel & Facilities
• Clubs & Activities
            """.strip()

    if "niet" in q:
        return """
NIET (Noida Institute of Engineering & Technology) is an AICTE-approved,
AKTU-affiliated institute known for B.Tech, MCA, MBA and more — with strong placement,
modern campus infrastructure, and active student clubs.

Ask specifically like:
• Why choose NIET?
• NIET infrastructure?
• NIET ranking?
• NIET hostel?
        """.strip()

    return ask_ollama_with_context(
        q,
        "Answer only about NIET institute overview. Do not hallucinate new claims."
    )


if __name__ == "__main__":
    print(about_niet_router("tell me about NIET"))
    print(about_niet_router("why choose niet"))
    print(about_niet_router("wifi "))
