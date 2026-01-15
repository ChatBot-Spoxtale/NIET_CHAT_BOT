import os ,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from RAG.router.club_router import club_router
from RAG.router.admission_router import admission_router
from Ollama.llm_client import ask_ollama_raw
from RAG.router.btech_course import btech_router
from RAG.router.mtech_course_router import mtech_router
from RAG.router.ug_pg_router import ug_pg_router
from RAG.router.facilities_router import facilities_router
from RAG.router.event_router import event_router
from RAG.router.niet_overview import about_niet_router

def answer_rag(query: str):
    q = query.lower().strip()

    # ---------- EVENTS ----------
    if any(w in q for w in ["event", "events", "hackathon", "conference"]):
        res = event_router(q)
        if res:
            return res
    
    # ---------- ADMISSION ----------
    if "admission" in q or "admissions" in q:
        admission=admission_router(q)
        if admission:
            return admission
        else:
            return "For More Information :- https://www.niet.co.in/admissions/eligibility-admission-process"

    if any(w in q for w in ["counselling", "jee", "direct admission", "fee", "documents","about","niet"]):
        res = about_niet_router(q)
        if res:
            return res
        return "For complete and up-to-date details regarding eligibility criteria and the admission process, kindly refer to the official NIET admissions page refer to the official NIET admissions page:\nhttps://www.niet.co.in/admissions/eligibility-admission-process"
    #------SYALLABUS-----
    if any(w in q for w in ["syllabus", "pdf", "subject", "subjects", "curriculum"]):
        return "To access the complete and officially updated course syllabus, please consult the official NIET syllabus page.:\nhttps://www.niet.co.in/academics/syllabus"
    
       # ---------- CLUBS ----------
    if "club" in q or "clubs" in q:
        res = club_router(q)
        if res:
            return res
        return "Visit:\nhttps://niet.co.in/students-life/student-clubs-societies"
    
    COURSE_KEYWORDS = [
    "btech", "b.tech", "mtech", "m.tech",
    "mba", "mca", "pharm", "b.pharm",
    "cse", "ece", "me", "civil", "ai", "ds","aiml"
]

    GENERIC_FACILITY_KEYWORDS = [
    "wifi",
    "non veg",
    "non-veg",
    "washing machine",
    "iron","aiml","ai","cy","me","ece","aiml","ai","cy","ds"
    ""
]
    # ---------- GENERIC FACILITY WITHOUT COURSE ----------
    if any(w in q for w in GENERIC_FACILITY_KEYWORDS):
        if not any(c in q for c in COURSE_KEYWORDS):
            return (
            "Could you please specify for which course or program you want this information?\n\n"
            "For example:\n"
            "- Admission Process\n"
            "- Btech CSE h\n"
            "- MBA\n"
            "- Hostel Facility"
        )

    # ---------- FACILITIES ----------
    res = facilities_router(q)
    if res:
        return res

    # ---------- BTECH ----------
    res = btech_router(q)
    if res:
        return res

    # ---------- MTECH ----------
    res = mtech_router(q)
    if res:
        return res

     # ---------- UG / PG ----------
    res = ug_pg_router(q)
    if res:
        return res
 


if __name__=="__main__":
    print(answer_rag("why choose iot"))
