import json
import os

# Project root directory (RAG/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path to club data JSON
DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data_chunk",
    "club_data_chunk",
    "club_chunks.json"
)

# Load club data once at startup
with open(DATA_PATH, "r", encoding="utf-8") as f:
    CLUB_DATA = json.load(f)

CLUB_LIST = {
    "Cultural & Hobby Clubs": [
        "Nritya Bhakti (Traditional Dance Club)",
        "Kathputliyaan (Theatre Club)",
        "Harmonics (Music Club)",
        "Spectrum (Cinematography Club)",
        "Megapixels (Photography & Videography Club)",
        "Green Gold Society",
        "Khushiyan Baaton Club",
        "Hope In Darkness (HID)",
    ],
    "Indoor Sports Clubs": [
        "Table Tennis Club",
        "Chess Club",
        "Dodge Gaming Club",
        "Yoga Club",
    ],
    "Outdoor Sports Clubs": [
        "Basketball Club",
        "Cricket Club",
        "Football Club",
        "Volleyball Club",
    ],
}

# QUERY NORMALIZATION
def club_normalize(query: str) -> str:
    """
    Normalizes user input so that:
    - Case differences don't matter
    - Extra symbols don't break matching
    - Common spelling mistakes are fixed
    - Similar phrases map to one standard form
    """
    q = query.lower().strip()

    # Remove punctuation that can break matching
    for ch in ["?", ",", ".", ":", "-", "_"]:
        q = q.replace(ch, " ")

    # Common spelling / wording corrections
    corrections = {
        "clubs":"club",
        "scoieties": "societies",
        "scoiety": "society",
        "hobyy": "hobby",
        "hobi": "hobby",
        "cultral": "cultural",
        "cutural": "cultural",
        "nritya bhkati": "nritya bhakti",
        "nritya bhaktiya": "nritya bhakti",
        "traditional":"nritya bhakti",

        "katputliyan": "kathputliyaan",
        "kathputliyan": "kathputliyaan",
        "hid ": "hope in darkness",
        "hope darkness": "hope in darkness",

        # IMPORTANT FIX for YOUR PROBLEM
        "khushiyan baton": "khushiyan baaton club",
        "khushiyan baaton": "khushiyan baaton club",
        "khushiyan batton": "khushiyan baaton club",
        "khushiya baaton": "khushiyan baaton club",
        
        #for spectrun
        "spectrum":"spectrum (cinematography ) club",
        "spectrum club":"spectrum (cinematography ) club",

        #megapixels
        "megapixels":"megapixels (photography & videography ) club",
        "megapixels club":"megapixels (photography & videography ) club",
        "photography club":"megapixels (photography & videography ) club",
        "videography club":"megapixels (photography & videography ) club",

        #green gold society
        "green gold society":"green gold society club",
        "green-gold-society":"green gold society club",

        #juventas club 
        "juventas club":"juventas (dance) club",
        "dance club":"juventas (dance) club",

        #harmonic club
        "harmonics club":"harmonics (music) club",
        "music club":"harmonics (music) club",

        #editorial club
        "editorial-club":"editorial club",
        "editorial  club":"editorial club",

        #yoga club
        "yoga-club":"yoga club",

        #dodge haming club
        "dodge gaming":"dodge gaming club",

        #chess club
        "chess-club":"chess club",

        #table tenn club
        "table tenn":"table tenn club",
        "table club":"table tenn club",

        #kathputliyaan club
        "kathputliyaan":"kathputliyaan club",
        "theatre club":"kathputliyaan club"
    }

    for wrong, right in corrections.items():
        q = q.replace(wrong, right)

    # Alias mapping (different words → same club)
    alias_map = {
        "dance club": "nritya bhakti",
        "traditional dance": "nritya bhakti",
        "theatre club": "kathputliyaan",
        "acting club": "kathputliyaan",
        "music club": "harmonics",
        "photography club": "megapixels",
        "videography club": "megapixels",
        "cinema club": "spectrum",
        "film club": "spectrum",
        "ngo club": "khushiyan baaton club",
        "social club": "khushiyan baaton club",
    }

    for key, value in alias_map.items():
        if key in q:
            q = value

    # Remove extra spaces
    return " ".join(q.split())


# CONSTANT CLUB GROUPS
 
OUTDOOR_CLUBS = [
    "Basketball Club",
    "Cricket Club",
    "Volleyball Club",
    "Football Club",
    "Sports Club",
]

INDOOR_CLUBS = [
    "Table Tennis Club",
    "Chess Club",
    "Dodge Gaming Club",
    "Yoga Club",
]

CULTURAL_CLUBS = [
    "Nritya Bhakti (Traditional Dance Club)",
    "Kathputliyaan (Theatre Club)",
    "Harmonics (Music Club)",
    "Spectrum (Cinematography Club)",
    "Megapixels (Photography & Videography Club)",
    "Green Gold Society",
    "Khushiyan Baaton Club",
    "Hope In Darkness (HID)",
]


# HELPER FUNCTION FOR FORMATTED LIST
def format_list(title: str, items: list) -> str:
    """
    Converts a list into a clean bullet-point response
    """
    bullets = "\n".join(f"• {item}" for item in items)
    return (
        f"{title}**\n"
        f"{bullets}\n\n"
        "🔗 Full list: https://niet.co.in/students-life/student-clubs-societies"
    )


#list of club format data 
def format_club_list() -> str:
    """
    Formats the hardcoded club list nicely
    """
    output = ["Here are the student clubs at NIET:\n"]
    for category, clubs in CLUB_LIST.items():
        output.append(f"{category}:")
        for club in clubs:
            output.append(f"• {club}")
        output.append("")  # empty line

    output.append("🔗 https://niet.co.in/students-life/student-clubs-societies")
    return "\n".join(output)

# MAIN ROUTER FUNCTION
def club_router(query: str):
    """
    Main entry point for club-related queries.
    Decides WHAT to answer based on the user question.
    """

    # Step 1: Normalize user query
    q = club_normalize(query)

    # CASE 1: User asks for list of clubs
    if "list" in q and "club" in q:
        return format_club_list()
    
    # CASE 2: Category-based queries
    if "outdoor" in q:
        return format_list("Outdoor Sports Clubs", OUTDOOR_CLUBS)

    if "indoor" in q:
        return format_list("Indoor Sports Clubs", INDOOR_CLUBS)

    if "cultural" in q or "hobby" in q or "activities" in q:
        return format_list("Cultural & Hobby Clubs", CULTURAL_CLUBS)

    # CASE 3: Exact club detail lookup
    for item in CLUB_DATA:
        name = item.get("club_name", "").lower()
        answer = item.get("answer", "")

        # Match full name or partial name safely
        if name == q or q in name or name in q:
            return answer

    # CASE 4: Keyword-based fallback
    for item in CLUB_DATA:
        for kw in item.get("keywords", []):
            if kw.lower() in q:
                return item.get("answer")

    # CASE 5: Final safe fallback
    club_names = [item["club_name"] for item in CLUB_DATA]
    return format_list("Available Clubs at NIET", club_names)


# LOCAL TESTING
if __name__ == "__main__":
    test_queries = [
        "list of clubs",
        # "indoor clubs",
        # "outdoor sports club",
        # "table tennis club",
        # "dance club",
        # "music club",
    ]

    for q in test_queries:
        print("Q:", q)
        print(club_router(q))
        print("-" * 50)
