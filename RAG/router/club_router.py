# RAG/routers/club_router.py
import json, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from Ollama.llm_client import ask_ollama_with_context


with open("RAG/data/club_chunks.json","r",encoding="utf-8") as f:
    CLUB_DATA = json.load(f)


def club_normalize(q: str) -> str:
    q = q.lower().strip()

    for ch in ["?", ",", ".", ":", "-"]:
        q = q.replace(ch, " ")

    corrections = {
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

    # alias mapping
    alias_map = {
        "dance club": "nritya bhakti",
        "traditional dance": "nritya bhakti",
        "theatre club": "kathputliyaan",
        "acting club": "kathputliyaan",
        "music club": "harmonics",
        "photography club": "megapixels",
        "film club": "spectrum",
        "cinema club": "spectrum",
        "social club": "khushiyan baaton club",
        "ngo club": "khushiyan baaton club",
    }

    for key, value in alias_map.items():
        if key in q:
            q = value

    return " ".join(q.split())


BAD_PATTERNS = [
    "student scoieties", "sports club(outdoor", "fitness club",
    "cultural and hooby", "different club", "how many club"
]


OUTDOOR = ["Basketball Club","Cricket Club","Volleyball Club","Football Club","Sports Club"]
INDOOR  = ["Table Tennis Club","Chess Club","Dodge Gaming Club","Yoga Club"]
CULTURAL = [
    "Nritya Bhakti (Traditional Dance)",
    "Kathputliyaan (Theatre Club)",
    "Harmonics (Music Club)",
    "Spectrum (Cinematography Club)",
    "Megapixels (Photography & Videography)",
    "Green Gold Society",
    "Khushiyan Baaton Club",
    "Hope In Darkness (HID)"
]


def format_list(title, arr):
    return f"{title}**\n" + "\n".join("• "+x for x in arr) + \
           "\n\n🔗 Full list: https://niet.co.in/students-life/student-clubs-societies"


def club_router(query: str):
    q = club_normalize(query)

    if "club" not in q and "society" not in q:
        return None

    if "outdoor" in q:
        return format_list("Outdoor Sports Clubs", OUTDOOR)

    if "indoor" in q:
        return format_list("Indoor Clubs", INDOOR)

    if "cultural" in q or "hobby" in q or "activities" in q:
        return format_list("Cultural & Hobby Clubs", CULTURAL)


    for item in CLUB_DATA:
        name = item.get("club_name","").lower()
        answer = item.get("answer","")

        if any(bad in name for bad in BAD_PATTERNS):
            continue  

        if name == q or name in q or q in name:
            return answer


    for item in CLUB_DATA:
        for kw in item.get("keywords", []):
            if kw.lower() in q:
                return item.get("answer")


    clean = [
        c["club_name"] for c in CLUB_DATA
        if not any(bad in c["club_name"].lower() for bad in BAD_PATTERNS)
    ]
    return format_list("Available Clubs at NIET", clean)



if __name__ == "__main__":
    test_queries = [
        # "list of clubs",
        # "outdoor sports club",
        # "indoor club list",
        # "cultural hobby club",
        # "nritya bhakti club",
        # "kathputliyaan club",
        # "Spectrum club"
        "green gold society"
    ]

    for q in test_queries:
        print(club_router(q))
