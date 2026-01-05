import os ,sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  

from RAG.router.syllabus_router import syllabus_router
from RAG.router.club_router import club_router
from RAG.router.about_course_router import about_course_router
from RAG.router.admission_router import admission_router
from RAG.router.faq_router import keyword_faq_router
from Ollama.llm_client import ask_ollama_raw
from RAG.router.course_router import course_router
from RAG.router.btech_course import btech_router
from RAG.router.mtech_course_router import mtech_router
from RAG.router.ug_pg_router import ug_pg_router
from RAG.router.facilities_router import facilities_router


def answer_rag(query:str):
    q=query.lower()

    facility_response = facilities_router(q)
    if facility_response:
        return facility_response
    
    if "about niet"in q or "niet" in q or "overview" in q:
        niet=keyword_faq_router(q)
        if niet:
            return niet
        else:
            "For more information visit:-https://www.niet.co.in/about"

    if any(w in q for w in ["syllabus", "pdf", "subject", "subjects", "curriculum"]):
        return "Please visit the official NIET syllabus page:\nhttps://www.niet.co.in/academics/syllabus"
    
    if "admission" in q or "admissions" in q or "quiry" in q or"counselling" in q or "jee main" in q or"admission process" in q:
        admission=admission_router(q)
        if admission:
            return admission
        else:
            "Please visit for more information:- https://www.niet.co.in/admissions/eligibility-admission-process"

    pg_ug = ug_pg_router(q)
    if pg_ug:
        return pg_ug
    

    course_response = btech_router(q)
    if course_response:
        return course_response
    

    mtech_course_response=mtech_router(q)
    if mtech_course_response:
        return mtech_course_response
    

    if "why choose" in q or "seats" in q or "seats" in q or "duration" in q or "durations" in q or "benefit" in q:
        course_overview=course_router(q)
        if course_overview:
            return course_overview
        else:
            "Please visit our website : - https://www.niet.co.in/courses"


    if "club" in q or "clubs" in q or "Club" in q or "Clubs":
        club=club_router(q)
        if club:
            return club
        else:
            "Please visit our website for more information:-  https://niet.co.in/students-life/student-clubs-societies "


    if "tell me "in q or "overview" in q or "course details" in q or "info" in q or "about" in q:
        about=about_course_router(q)
        if about :
            return about
        else:
            "Please visit our website :- https://www.niet.co.in/"
            ""

    

    return ask_ollama_raw(keyword_faq_router(q)) 


if __name__=="__main__":
    print(answer_rag("why choose iot"))
