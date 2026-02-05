import json
import os

# ---------- Load Research Chunk Data ----------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data_chunk",
    "overview_research_data_chunk",
    "overview_research_chunks.json"
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    RESEARCH_DATA = json.load(f)   # LIST

OFFICIAL_RESEARCH_URL = "https://www.niet.co.in/research/overview"


# ---------- Helpers ----------
def normalize(q: str) -> str:
    q = q.lower().strip()
    for ch in ["?", ",", ".", "-", "_"]:
        q = q.replace(ch, " ")
    return " ".join(q.split())


def bullets_from_lines(lines):
    return "\n".join(f"• {line}" for line in lines if line.strip())


def bullets_simple(text: str):
    """
    For non-project text (overview, areas, publications)
    """
    lines = [l.strip() for l in text.split(",") if l.strip()]
    return bullets_from_lines(lines)


def parse_project_answer(text: str):
    """
    Extract Domain / Faculty / Funding / Year safely
    """
    fields = []
    for part in text.split("."):
        part = part.strip()
        if part.lower().startswith(("domain", "faculty", "funding", "year")):
            fields.append(part)
    return fields


# ---------- Main Router ----------
def research_router(query: str):
    q = normalize(query)

    # 🔹 FULL research (explicit request only)
    if any(k in q for k in [
        "research at niet",
        "full research",
        "research summary",
        "research details",
        "research information",
        "research overview",
        "research",
    ]):
        blocks = []

        for item in RESEARCH_DATA:
            if item["chunk_id"].startswith("research_project"):
                bullets = parse_project_answer(item["answer"])
                blocks.append(
                    "📌 Research Project\n" + bullets_from_lines(bullets)
                )
            elif item["chunk_id"].startswith("research"):
                blocks.append(
                    "📌 Research Information\n" + bullets_simple(item["answer"])
                )

        return (
            "📌 Research at NIET\n\n"
            + "\n\n".join(blocks)
            + f"\n\n🔗 Official Research Page:\n{OFFICIAL_RESEARCH_URL}"
        )

    # 🔹 PROJECTS (special handling)
    if any(k in q for k in ["project", "projects", "funding", "grant"]):
        blocks = []

        for item in RESEARCH_DATA:
            if item["chunk_id"].startswith("research_project"):
                bullets = parse_project_answer(item["answer"])
                blocks.append(
                    "📌 Research Project\n" + bullets_from_lines(bullets)
                )

        if blocks:
            return (
                "📌 Research Projects at NIET\n\n"
                + "\n\n".join(blocks)
                + f"\n\n🔗 Official Research Page:\n{OFFICIAL_RESEARCH_URL}"
            )

    # 🔹 OTHER INDIVIDUAL INTENTS
    INTENT_MAP = {
        "overview": "overview",
        "area": "areas",
        "areas": "areas",
        "publication": "publications",
        "paper": "publications",
        "journal": "journals",
    }

    for word, intent in INTENT_MAP.items():
        if word in q:
            for item in RESEARCH_DATA:
                if intent in item.get("keywords", []):
                    return (
                        f"📌 Research {intent.capitalize()} at NIET\n\n"
                        + bullets_simple(item["answer"])
                        + f"\n\n🔗 Official Research Page:\n{OFFICIAL_RESEARCH_URL}"
                    )

    # 🔹 Fallback generic research
    if "research" in q:
        answers = []

        for item in RESEARCH_DATA:
            if item["chunk_id"].startswith("research"):
                answers.append(bullets_simple(item["answer"]))

        return (
            "📌 Research at NIET\n\n"
            + "\n\n".join(answers)
            + f"\n\n🔗 Official Research Page:\n{OFFICIAL_RESEARCH_URL}"
        )

    return None