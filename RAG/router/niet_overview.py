# RAG/routers/about_niet_router.py
import json, os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from Ollama.llm_client import ask_ollama_with_context

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "combined_chunks.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
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

RESEARCH_TRIGGERS = [
    "research",
    "research area",
    "research areas",
    "research focus",
    "research at niet",
    "niet research",
    "r&d",
    "innovation research"
]

ADMISSION_TRIGGERS = [
    "admission",
    "admission process",
    "how to apply",
    "direct admission",
    "niet admission",
    "fee",
    "documents",
    "eligibility",
    "college fee",
    "education loan"
]

def about_niet_router(query: str):
    q = normalize(query)

    # ---------- RESEARCH ----------
    if any(trigger in q for trigger in RESEARCH_TRIGGERS):
        for item in NIET_DATA:
            question = normalize(item.get("question", ""))
            if "research" in question:
                return f"""
🔬 Research at NIET
{item.get("answer")}
                """.strip()
            
    if any(trigger in q for trigger in ADMISSION_TRIGGERS):
        responses = []

        for item in NIET_DATA:
            question = normalize(item.get("question", ""))
            if any(key in question for key in ["admission", "apply", "documents", "fee", "loan"]):
                responses.append(f"• {item.get('answer')}")

        if responses:
            return f"""
🎓 Admission Information – NIET
{chr(10).join(responses)}

🔗 Apply here: https://applynow.niet.co.in/
📞 Admission Helpline: 8010500700
        """.strip()

    # ---------- ABOUT NIET ----------
    if not any(trigger in q for trigger in ABOUT_TRIGGERS):
        return None

    for item in NIET_DATA:
        question = normalize(item.get("question", ""))
        ans = item.get("answer", "")

        if any(word in question for word in q.split()):
            return f"""
About NIET
{ans}


            """.strip()

    # ---------- FALLBACK ----------
    if "niet" in q:
        return """
NIET (Noida Institute of Engineering & Technology) is an AICTE-approved,
AKTU-affiliated autonomous institute known for strong placements,
modern infrastructure, and active research culture.

Ask specifically:
• Research areas at NIET
• Why choose NIET?
• NIET rankings
• NIET hostel
        """.strip()

    return ask_ollama_with_context(
        q,
        "Answer only about NIET institute overview. Do not hallucinate."
    )


if __name__ == "__main__":
    print(about_niet_router("tell me about NIET"))
    print(about_niet_router("why choose niet"))
