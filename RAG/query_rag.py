import re
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from router.btech_router import btech_router
from router.event_router import event_router
from router.club_router import club_router
from router.facilities_router import facility_router
from router.mtech_router import mtech_router
from router.ug_pg_router import ug_pg_router
from router.institute_router import institute_router
from router.admission_router import admission_router
from router.research_router import research_router 

def answer_rag(query: str) -> str:
    q = query.lower().strip()

    if "research" in q:
        res=research_router(q)
        if isinstance(res,str) and res.strip():
            return res
    
    res = facility_router(q)
    if isinstance(res, str) and res.strip():
        return res

    if any(k in q for k in ["list","club", "clubs", "society", "societies"]):
        res = club_router(q)
        if isinstance(res, str) and res.strip():
            return res
        return (
            "Please visit the official NIET Clubs & Societies page:\n"
            "https://niet.co.in/students-life/student-clubs-societies"
        )

    if any(w in q for w in ["event", "events", "hackathon", "conference"]):
        res = event_router(q)
        if isinstance(res, str) and res.strip():
            return res
        
    if "admission" in q:
        res=admission_router(q)
        if isinstance(res, str) and res.strip():
            return res
    
    res = institute_router(q)
    if isinstance(res, str) and res.strip():
        return res
        

    res = mtech_router(q)
    if isinstance(res, str) and res.strip():
        return res

    res = ug_pg_router(q)
    if isinstance(res, str) and res.strip():
        return res

    TWINNING_KEYWORDS = [
        "twinning",
        "international",
        "abroad",
        "foreign",
        "semester abroad"
    ]

    if any(k in q for k in TWINNING_KEYWORDS):
        twinning = twinning_router(q)
        if twinning:
            return twinning


    if any(w in q for w in ["syllabus", "pdf", "subject", "subjects", "curriculum"]):
        return (
            "To access the complete and officially updated course syllabus, "
            "please visit:\nhttps://www.niet.co.in/academics/syllabus"
        )

    BTECH_KEYWORDS = {
        "btech", "b.tech",
        "cse", "aiml", "ai",
        "data science", "cyber security",
        "iot", "ece", "me", "bio"
    }

    words = set(re.findall(r"[a-z]+", q))
    if words.intersection(BTECH_KEYWORDS):
        res = btech_router(q)
        if isinstance(res, str) and res.strip():
            return res
            

    

