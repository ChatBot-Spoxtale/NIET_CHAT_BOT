# RAG/routers/syllabus_router.py
import json
from RAG.alias_map.alias_map import DEPT_ALIASES  

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  
DATA_PATH = BASE_DIR / "data" / "url_final_chunks.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    SYLLABUS_DATA = f.read()


def normalize_query(q: str):
    q = q.lower().strip()

    corrections = {
        "syllb": "syllabus",
        "syll": "syllabus",
        "subjet": "subject",
        "aiml ": "aiml",
        "ai ml": "aiml",
        "aml": "aiml",
        "cse aiml": "aiml",
        "cse ml": "aiml",
        "btech": "b.tech",
        "btch": "b.tech",
        "ds ":"data science",
        "csbs ": "csbs",
        "cse ds": "data science",
        "it ": "information technology",
    }

    for wrong, right in corrections.items():
        q = q.replace(wrong, right)

    return q


def detect_department(q: str):
    q = q.lower()
    for dept, aliases in DEPT_ALIASES.items():
        for alias in aliases:
            if alias in q:
                return dept
    return None  

import re

def extract_url(text: str):
    if not text: return None
    match = re.search(r'https?://\S+', text)
    return match.group(0).strip() if match else None


def syllabus_router(query: str):
    q = query.lower().strip()

    if not any(word in q for word in ["syllabus", "pdf", "subject", "subjects", "course structure"]):
        return None

    if "twinning" in q:
        if "it" in q or "it twinning" in q:
                      return """
B.Tech IT Twinning Syllabus (NIET)
https://www.niet.co.in/assets/frontend/pdf/B.Tech-in-Information-Technology-IT-Twinning-First-Year-2024-25.pdf"""

    if "mtech" in  q:
        if ("cse" in q) and not any(x in q for x in ["aiml", "ds", "cy","ai","iot"]):
            return """
M.Tech CSE Syllabus (NIET)
No official syllabus URL was provided for MTECH CSE. Contact NIET Academics for updated links https://www.niet.co.in/academics/syllabus
"""
        #Biotech
        elif "bio" in q or "biotech" in q:
            return """
M.Tech BIOTECH Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/M.%20Tech%20in%20Biotechnology%20_BT_%20First%20Year%202023-24.pdf"""

        elif "vlsi" in q :
            return """
M.Tech VLSI Syllabus :-
https://www.niet.co.in/assets/frontend/pdf/mtech-vlsi-first.pdf"""

        elif "ai" in q or "cse ai" in q:
            return """
M.Tech AI Syllabus :-
https://www.niet.co.in/assets/frontend/pdf/M.Tech.%20in%20Artificial%20Intelligence%20_AI_%20First%20Year%202023-24.pdf"""

        elif "me" in q :
            return """
M.Tech ME Syllabus :-
https://www.niet.co.in/assets/frontend/pdf/M.%20Tech%20in%20Mechanical%20Engineering%20_ME_%20First%20Year%202023-24.pdf"""


    #BTECH SYllabus
    if ("cse" in q) and not any(x in q for x in ["aiml", "ds", "cy","ai","iot"]):
        return """
B.Tech CSE Syllabus (NIET):-
https://niet.co.in/assets/frontend/pdf/B.Tech-CSE-First-Year-2024-25.pdf
"""

    # CSE - AIML
    elif "aiml" in q or "cse aiml" in q or "ai ml" in q:
        return """
B.Tech CSE (AIML) Syllabus
 https://niet.co.in/assets/frontend/pdf/B.Tech-AIML-First-Year-2024-25.pdf
"""
    #CSE AI
    elif "ai" in q or "cse ai" in q or "ai" in q or "artificial intelligence" in q:
        return """
B.Tech CSE (AI) Syllabus:-
 https://www.niet.co.in/assets/frontend/pdf/B.Tech-in-Computer-Science-and-Engineering-Artificial-Intelligence-First-Year-AIAI.pdf
"""

    # CSE - Data Science (DS)
    elif "ds" in q or "data science" in q or "cse ds" in q:
        return """
B.Tech CSE (Data Science) Syllabus:-
 https://www.niet.co.in/assets/frontend/pdf/B.Tech-in-Computer-Science-and-Engineering(Data-Science)(DS)-First-Year-2024-25.pdf
"""

    # IoT
    elif "iot" in q or "internet of things" in q :
        return """
B.Tech IoT Syllabus
https://niet.co.in/assets/frontend/pdf/B.Tech-IoT-First-Year-2024-25.pdf
"""

    # Cyber Security
    elif "cy" in q or "cyber security" in q or "cse cy" in q:
        return """
B.Tech CSE CY Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/B.Tech-in-Computer-Science-and-Engineering(Cyber%20Security)(CY)-First-Year-2024-25.pdf"""

    #vlsi
    elif "vlsi" in q:
        return """
Vlsi Syllabus:- 
https://niet.co.in/assets/frontend/pdf/B.Tech-ECE-VLSI-2024-25.pdf"""

    # CSBS
    elif "csbs" in q or "business system" in q:
        return """
CSBS Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/B.Tech-in-Computer-Science-and-Business-System(CSBS)-First-Year-2024-25.pdf
"""
    #Btech ECE
    elif "ece" in q:
        return """
B.TECH ECE Syllabus:-
No official syllabus URL was provided for BTECH ECE. Contact NIET Academics for updated links."""

    #BCA
    elif "mba" in q:
        return """
BCA Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/Bachelor-of-Computer-Applications-(BCA)-First-Year-2024-25.pdff
"""

    # MCA
    elif "mca" in q:
        return """
MCA Syllabus :-
https://www.niet.co.in/assets/frontend/pdf/Master%20of%20Computer%20Applications%20(MCA)%20First%20Year%202024-25.pdf"""

    # MBA
    elif "mba" in q:
        return """
MBA Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/Masters-of-Business-Administration-Innovation-Entrepreneurship-and-Venture-Development-MBA-IEV-First-Year-2023-24.pd
"""
 # MBA
    elif "mca integrated" in q:
        return """
MCA Integrated Syllabus: -
https://www.niet.co.in/assets/frontend/pdf/MCA(Integrated)%20First%20Year%20Syllabus%202024-25.pdf"""

#minor degree aiml
    elif "minor degree aiml" in q or "minor degree" in q:
        return """
MBA Syllabus:-
https://www.niet.co.in/assets/frontend/pdf/AIML-Minor-Degree-Specialization-Scheme-2022-23.pdf"""
    return """
I found your query but couldn't detect exact branch.

Please ask like:
• **BTech CSE syllabus pdf**
• **CSE AIML syllabus**
• **CSE DS syllabus pdf**
• **BTech IoT syllabus**

Or check official list:
👉 https://www.niet.co.in/academics/syllabus
"""


if __name__ == "__main__":
    tests = [
        "btech cse syllabus",
        "syllabus for btech cse ds",
        "btech cse aiml pdf",
        "iot syllabus pdf",
        "cse cyber security syllabus",
        "csbs syllabus",
        "syllabus for btech cse it twinning",
        "syllabus for mtech cse ai",

    ]
    for t in tests:
        print(syllabus_router(t))
