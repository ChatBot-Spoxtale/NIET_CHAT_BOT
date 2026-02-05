import re

# =====================================================
# 🔹 ALL TWINNING DATA (INLINE – SINGLE SOURCE OF TRUTH)
# =====================================================

TWINNING_PROGRAMS = [
    {
        "course": "B.Tech CSE Artificial Intelligence – International Twinning",
        "branch": "cse",
        "specialization": "ai",
        "keywords": [
            "cse ai twinning",
            "artificial intelligence international",
            "ai twinning",
            "international cse ai"
        ],
        "overview": (
            "The International Twinning Program in Artificial Intelligence allows students "
            "to complete part of their degree at a partner foreign university. "
            "This program offers global exposure, international curriculum, and credit transfer."
        ),
        "properties": {
            "duration": "4 Years",
            "seats": "Varies",
            "eligibility": "10+2 PCM + JEE/UPTAC + Passport",
            "fees": "As per NIET & partner university norms"
        },
        "why_choose": [
            "Study one or more semesters abroad",
            "International curriculum and exposure",
            "Credit transfer from foreign university",
            "Improved global career opportunities"
        ]
    },
    {
        "course": "B.Tech CSE AIML – International Twinning",
        "branch": "cse",
        "specialization": "aiml",
        "keywords": [
            "cse aiml twinning",
            "aiml international",
            "artificial intelligence machine learning twinning"
        ],
        "overview": (
            "This International Twinning program focuses on Artificial Intelligence "
            "and Machine Learning with an opportunity to study abroad at a partner university."
        ),
        "properties": {
            "duration": "4 Years",
            "seats": "Varies",
            "eligibility": "10+2 PCM + JEE/UPTAC + Passport",
            "fees": "As per NIET & partner university norms"
        },
        "why_choose": [
            "Global exposure in AI & ML",
            "Advanced international labs and curriculum",
            "Strong overseas career prospects"
        ]
    },
    {
        "course": "B.Tech Information Technology – International Twinning",
        "branch": "it",
        "specialization": "",
        "keywords": [
            "it twinning",
            "information technology international",
            "btech it twinning"
        ],
        "overview": (
            "The IT International Twinning Program provides students with an opportunity "
            "to gain global exposure by studying abroad while completing their B.Tech degree."
        ),
        "properties": {
            "duration": "4 Years",
            "seats": "Varies",
            "eligibility": "10+2 PCM + JEE/UPTAC + Passport",
            "fees": "As per NIET & partner university norms"
        },
        "why_choose": [
            "Study IT in a global academic environment",
            "International exposure and cultural learning",
            "Better placement opportunities abroad"
        ]
    },
]

# =====================================================
# 🔹 HELPERS
# =====================================================

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def is_twinning_query(query: str) -> bool:
    q = normalize(query)
    return any(word in q for word in [
        "twinning",
        "international",
        "abroad",
        "foreign"
    ])


# =====================================================
# 🔹 FORMATTER
# =====================================================

def format_twinning(course: dict) -> str:
    p = course.get("properties", {})

    return f"""
🌍 *{course.get('course')}*

📘 *Overview*
{course.get('overview')}

📌 *Program Details*
• Duration: {p.get('duration', 'NA')}
• Seats: {p.get('seats', 'NA')}
• Eligibility: {p.get('eligibility', 'NA')}
• Fees: {p.get('fees', 'NA')}

⭐ *Why Choose This Twinning Program?*
- """ + "\n- ".join(course.get("why_choose", []))


# =====================================================
# 🔹 MAIN ROUTER
# =====================================================

def twinning_router(query: str):
    if not is_twinning_query(query):
        return None

    q = normalize(query)
    results = []

    for program in TWINNING_PROGRAMS:
        text = " ".join([
            program.get("course", ""),
            program.get("branch", ""),
            program.get("specialization", ""),
            " ".join(program.get("keywords", []))
        ])

        if any(word in normalize(text) for word in q.split()):
            results.append(program)

    # fallback → return all twinning programs
    if not results:
        results = TWINNING_PROGRAMS

    return "\n\n".join(format_twinning(p) for p in results)


# =====================================================
# 🔹 LOCAL TEST
# =====================================================

if __name__ == "__main__":
    tests = [
        "twinning program",
        "btech cse twinning",
        "aiml international",
        "it international program"
    ]

    for t in tests:
        print("\nQ:", t)
        print(twinning_router(t))
