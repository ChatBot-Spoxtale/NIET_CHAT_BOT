import os ,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from RAG.router.club_router import club_router
from RAG.router.admission_router import admission_router
# from RAG.router.faq_router import keyword_faq_router
# from RAG.router.course_router import course_router
from RAG.router.btech_course import btech_router
from RAG.router.mtech_course_router import mtech_router
from RAG.router.ug_pg_router import ug_pg_router
from RAG.router.facilities_router import facilities_router
from RAG.router.event_router import event_router
from RAG.router.niet_overview import about_niet_router

def answer_rag(query: str):
    q = query.lower().strip()
    if "admission" in q or "admissions" in q:
        admission = admission_router(q)
        if admission:
            return admission
        return (
            "For complete admission details, please visit:\n"
            "https://www.niet.co.in/admissions/eligibility-admission-process"
        )
        
    if any(w in q for w in ["syllabus", "pdf", "subject", "subjects", "curriculum"]):
        return (
            "To access the complete and officially updated course syllabus, "
            "please consult the official NIET syllabus page:\n"
            "https://www.niet.co.in/academics/syllabus"
        )
     # ---------- NIET OVERVIEW (LAST) ----------
    if any(w in q for w in ["about", "niet", "institute", "college"]):
        res = about_niet_router(q)
        if res:
            return res
        return (
            "For official information about NIET, please visit:\n"
            "https://www.niet.co.in"
        )
    if any(w in q for w in ["event", "events", "hackathon", "conference"]):
        res = event_router(q)
        if res:
            return res

    if "club" in q or "clubs" in q:
        res = club_router(q)
        if res:
            return res
        return "Visit:\nhttps://niet.co.in/students-life/student-clubs-societies"

    res = facilities_router(q)
    if res:
        return res
    res = ug_pg_router(q)
    if res:
        return res

    res = btech_router(q)
    if res:
        return res

    res = mtech_router(q)
    if res:
        return res

   

    return (
        "I couldn’t find a specific answer to that.\n\n"
        "You may explore official information here:\n"
        "https://www.niet.co.in"
    )



if __name__=="__main__":
    print(answer_rag("why choose iot"))

