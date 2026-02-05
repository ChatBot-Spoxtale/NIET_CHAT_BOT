import re

TWINNING_PROGRAMS = [
    {
        "course": "B.Tech CSE (Artificial Intelligence – International Twinning)",
        "branch": "cse",
        "specialization": "twinning",
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
        "specialization": "twinning",
        "keywords": [
            "aiml ",
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
        "specialization": "twinning",
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
    {
    "course": "B.Tech Computer Science Engineering – International Twinning",
    "branch": "cse",
    "specialization": "twinning",
    "keywords": [
        "cse international twinning",
        "computer science engineering international",
        "cse international program",
        "cse twinning",
        "international cse"
    ],
    "overview": (
        "Make your academic journey truly international. "
        "NIET offers an AICTE-approved International Twinning program in "
        "Computer Science Engineering, built on strong institution-to-institution "
        "partnerships. The program enables students to study part of their degree "
        "at a foreign partner university, providing global exposure, enhanced "
        "learning opportunities, and affordable access to international education."
    ),
    "properties": {
        "duration": "4 Years",
        "seats": "Varies",
        "mode": "Full Time",
        "eligibility": "10+2 PCM + JEE/UPTAC + Valid Passport",
        "fees": "As per NIET & partner university norms"
    },
    "why_choose": [
        "Spend a semester abroad and experience global education",
        "Credits earned at the foreign university are transferred to NIET",
        "AICTE-approved international academic structure",
        "Better global career and higher education opportunities"
    ],
    "placements": {
        "placements_offered": "640",
        "highest_package": "40 LPA",
        "average_package": "5.68 LPA",
        "source_url": "https://niet.co.in/department/computer-science-engineering/placement"
    },
    "source_url": "https://niet.co.in/course/b-tech-computer-science-engineering-international-twinning-program"
}
]

# HELPERS

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

def twinning_router(query: str):
    if not is_twinning_query(query):
        return None

    q = normalize(query)

    specialization_intent = None
    if "aiml" in q or "machine learning" in q:
        specialization_intent = "aiml"
    elif "artificial intelligence" in q or " ai " in f" {q} ":
        specialization_intent = "ai"
    elif "information technology" in q or " it " in f" {q} ":
        specialization_intent = "it"

    branch_intent = None
    if "cse" in q or "computer science" in q:
        branch_intent = "cse"
    elif "information technology" in q or " it " in f" {q} ":
        branch_intent = "it"

    if specialization_intent and branch_intent:
        for program in TWINNING_PROGRAMS:
            text = normalize(
                program.get("course", "") + " " + " ".join(program.get("keywords", []))
            )

            if (
                specialization_intent in text
                and branch_intent == program.get("branch")
            ):
                return format_twinning(program)  

    if branch_intent == "cse" and not specialization_intent:
        results = [
            p for p in TWINNING_PROGRAMS
            if p.get("branch") == "cse"
        ]

        if results:
            return "\n\n".join(format_twinning(p) for p in results)

    if branch_intent == "it":
        for program in TWINNING_PROGRAMS:
            if program.get("branch") == "it":
                return format_twinning(program)

    results = []
    for program in TWINNING_PROGRAMS:
        keywords = normalize(" ".join(program.get("keywords", [])))
        if any(k in q for k in keywords.split()):
            results.append(program)

    if results:
        return "\n\n".join(format_twinning(p) for p in results)

    return "\n\n".join(format_twinning(p) for p in TWINNING_PROGRAMS)

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