# RAG/router/admission_router.py

import json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

BASE_DIR = Path(__file__).resolve().parent.parent  
DATA_PATH = BASE_DIR / "data" / "admission_chunks.json"


def clean_text(text: str):
    """Normalize input for better matching"""
    replace_map = {
        "-": " ",
        ".": " ",
        "&": " and ",
        "(": " ",
        ")": " ",
        ",": " ",
    }
    text = text.lower()
    for old, new in replace_map.items():
        text = text.replace(old, new)
    return " ".join(text.split())


PRIORITY_MAP = [
    ("btech it", "btech it"),
    ("b tech it", "btech it"),
    ("information technology", "btech it"),

    ("btech cse", "btech cse"),
    ("computer science engineering", "btech cse"),

    ("btech", "first year  btech"),   

    ("mca", "first year  mca"),
    ("master of computer applications", "first year  mca"),

    ("mba", "first year  mba"),
    ("business administration", "first year  mba"),

    ("lateral entry btech", "lateral entry btech"),
    ("lateral entry", "lateral entry btech"),

    ("b.pharm", "first year  b.pharm"),
    ("pharmacy", "first year  b.pharm"),

    ("pgdm", "for admission to pgdm course"),
    ("m.tech", "for admission to m.tech course"),
    ("mtech", "for admission to m.tech course"),

    ("twinning", "twinning_program"),
]


def admission_router(query: str):
    q = clean_text(query)

    TRIGGERS = ["admission", "admission process", "how to take", "how to apply"]
    if not any(t in q for t in TRIGGERS):
        return None

    if "btech" in q or "b tech" in q:
        for row in ADMISSION_DATA:
            if "first year  btech" in row["course"].lower().replace(" ", ""):
                return format_admission(row)

    for key, tag in PRIORITY_MAP:
        if key in q:
            for row in ADMISSION_DATA:
                if tag.replace(" ", "") in row["course"].replace(" ", "").lower():
                    return format_admission(row)

    return """
Admission details for the selected course are not available.

Please check spelling OR try:
• admission process for btech
• admission process for mca
• admission for mba
• admission for pgdm
    """.strip()


def format_admission(row):
    return f"""
Admission Process for {row['course']}
{row['answer']}

"""


if __name__ == "__main__":
    print(admission_router("admission process for btech it"))
    print(admission_router("how to take admission in MCA"))
    print(admission_router("b.tech cse admission process"))
    print(admission_router("how to take admission in PGDM"))

