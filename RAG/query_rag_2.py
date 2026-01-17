import os ,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from RAG.router.club_router import club_router
from RAG.router.btech_course import btech_router
from RAG.router.mtech_course_router import mtech_router
from RAG.router.ug_pg_router import ug_pg_router
from RAG.router.facilities_router import facilities_router
from RAG.router.event_router import event_router
from RAG.router.niet_overview import about_niet_router
from RAG.router.admission_router import admission_router


def answer_rag(query: str):
    q = query.lower().strip()

    BTECH_SPECIALIZATIONS = [
    "aiml", "ai", "artificial intelligence",
    "data science", "ds",
    "cyber", "cyber security","cy",
    "iot", "internet of things","me","ece","bio","it"
]

    is_btech = (
    "btech" in q
    or "b.tech" in q
    or any(s in q for s in BTECH_SPECIALIZATIONS)
)
    is_mtech = "mtech" in q or "m.tech" in q

    # ---------- SYLLABUS (highest priority) ----------
    if any(w in q for w in ["syllabus", "pdf", "subject", "subjects", "curriculum"]):
        return (
            "To access the complete and officially updated course syllabus, "
            "please consult the official NIET syllabus page:\n"
            "https://www.niet.co.in/academics/syllabus"
        )
    
    # ---------- ADMISSION ----------
    if "admission" in q or "admissions" in q:
        admission = admission_router(q)
        if admission:
            return admission
        return (
            "For complete admission details, please visit:\n"
            "https://www.niet.co.in/admissions/eligibility-admission-process"
        )
    if any(w in q for w in ["event", "events", "hackathon", "conference"]):
        res = event_router(q)
        if res:
            return res

     # ---------- NIET OVERVIEW (LAST) ----------
    if any(w in q for w in ["about", "niet", "institute", "college"]):
        res = about_niet_router(q)
        if res:
            return res
        return (
            "For official information about NIET, please visit:\n"
            "https://www.niet.co.in"
        )
    # ---------- EVENTS ----------
    
    # ---------- CLUBS ----------
    if "club" in q or "clubs" in q:
        res = club_router(q)
        if res:
            return res
        return "Visit:\nhttps://niet.co.in/students-life/student-clubs-societies"

    FACILITY_KEYWORDS = [
    "facility", "facilities", "infrastructure",
    "campus", "hostel", "sports", "gym",
    "health", "library", "labs", "academic facilities","medical facilities"
]

    if any(k in q for k in FACILITY_KEYWORDS):
        res = facilities_router(q)
        if res:
            return res
        return (
        "For detailed and up-to-date information about NIET facilities, "
        "please visit the official pages below:\n\n"
        "Sports & Health Facilities\n"
        "- https://www.niet.co.in/sports-health-facilities/sports\n\n"
        "Academic Facilities\n"
        "- https://www.niet.co.in/sports-health-facilities/sports\n\n"
        "Campus Infrastructure\n"
        "- https://www.niet.co.in/infrastructure/campus-facilities"
    )
  # ---------- BTECH (highest priority for UG engineering) ----------
    if is_btech:
        res = btech_router(q)
        if res:
            return res

# ---------- MTECH ----------
    if is_mtech:
        res = mtech_router(q)
        if res:
            return res

# ---------- UG / PG (MBA / MCA / BBA only) ----------
    if not is_btech and not is_mtech:
        res = ug_pg_router(q)
        if res:
            return res


    # ---------- FALLBACK ----------
    return (
        "I couldn’t find a specific answer to that.\n\n"
        "You may explore official information here:\n"
        "https://www.niet.co.in"
    )



if __name__=="__main__":
    print(answer_rag("why choose iot"))



