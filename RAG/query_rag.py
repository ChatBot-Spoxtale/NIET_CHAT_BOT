import os,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from router.btech_router import btech_router
from router.event_router import event_router
from router.club_router import club_router
from router.facilities_router import facility_router
def answer_rag (query:str):
    q = query.lower().strip()
    answer = facility_router(q)
    if answer:
        return answer

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

    if is_btech:
        res = btech_router(q)
        if res:
            return res
        
    if any(w in q for w in ["event", "events", "hackathon", "conference"]):
        res = event_router(q)
        if res:
            return res
    
    if "club" in q or "clubs" in q:
        res = club_router(q)
        if res:
            return res
        return "Visit:\nhttps://niet.co.in/students-life/student-clubs-societies"

   