import json
import re
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parents[2]

COURSE_CHUNK_DIR = BASE_DIR / "data_chunk" / "course_data_chunk"
FACILITY_CHUNK_DIR = BASE_DIR / "data_chunk" / "facilities_data_chunk"
CLUB_CHUNK_DIR = BASE_DIR / "data_chunk" / "club_data_chunk"
OVERVIEW_RESEARCH_DIR=BASE_DIR/ "data_chunk" / "overview_research_data_chunk"
ADMISSION_CHUNK_DIR = BASE_DIR / "data_chunk" / "admission_data_chunk"
EVENT_CHUNK_DIR=BASE_DIR/ "data_chunk"/ "event_data_chunk"
GENERAL_CHUNK_DIR=BASE_DIR/"data_chunk"/"general_question_chunk"


ALIAS_MAP= {
    "aiml": ["aiml","ai ml","cse aiml","btech aiml","b.tech aiml","artificial intelligence","ai & ml"],
    "cse": ["cse","cs","computer science","btech cse","b.tech cse"],
    "ds": ["ds","data science","btech ds","cse ds","b.tech ds"],
    "iot": ["iot","internet of things","btech iot","b.tech iot"],
    "csbs": ["csbs","computer science business system"],
    "cy": ["cyber security","cse cy","cs cyber","btech cyber"],
    "mca": ["mca","master of computer application"],
    "mba": ["mba","master of business administration"],
    "mechanical": ["mechanical", "me", "mech", "mechanical engineering", "btech me", "b tech me"],
}

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def load_chunks_from_dir(directory: Path) -> List[Dict]:
    chunks = []

    if not directory.exists():
        return chunks

    for file in directory.glob("*_chunks.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    chunks.extend(data)
        except Exception as e:
            print(f"Failed to load {file.name}: {e}")

    return chunks

def expand_query(query: str) -> str:
    expanded = query
    for short, full in ALIAS_MAP.items():
        if short in query:
            expanded += " " + " ".join(full)
    return expanded

def detect_source(query: str) -> str:
    q = query.lower()

    if any(w in q for w in [
        "why should", "why choose", "why take",
        "is niet good", "is it good",
        "worth it", "why niet"
    ]):
        return "general"
    
    if any(w in q for w in [
    "placement", "placements",
    "package", "highest", "average", "record"
]):
        return "course"

    if any(w in q for w in [
    "admission", "admissions", "eligibility", "criteria",
    "direct admission", "lateral entry", "counseling",
    "jee", "upcet", "uptac"
]):
        return "admission"

    if any(w in q for w in ["club", "clubs", "society", "activity"]):
        return "club"

    if any(w in q for w in ["event", "events", "happening"]):
        return "event"

    if any(w in q for w in ["hostel", "library", "facility", "lab"]):
        return "facility"

    if any(w in q for w in ["ranking", "rank", "research", "project"]):
        return "overview"
    if any(k in q for k in ALIAS_MAP.keys()):
        return "course"
    return "all"


def retrieve_chunks(query: str, top_k: int = 3) -> List[Dict]:
    query = normalize(query)
    query = expand_query(query)
    source = detect_source(query)


    chunks = []
    # if "admission" in query:
        # return load_chunks_from_dir(ADMISSION_CHUNK_DIR)[:top_k]

    if source in ("course", "all"):
        chunks.extend(load_chunks_from_dir(COURSE_CHUNK_DIR))

    if source in ("facility", "all"):
        chunks.extend(load_chunks_from_dir(FACILITY_CHUNK_DIR))

    if source in ("club", "all"):
        chunks.extend(load_chunks_from_dir(CLUB_CHUNK_DIR))

    if source in ("overview", "all"):
        chunks.extend(load_chunks_from_dir(OVERVIEW_RESEARCH_DIR))
    if source in ("admission", "all"):
        chunks.extend(load_chunks_from_dir(ADMISSION_CHUNK_DIR))

    if source in ("event","all"):
        chunks.extend(load_chunks_from_dir(EVENT_CHUNK_DIR))

    if source in ("general", "all"):
        chunks.extend(load_chunks_from_dir(GENERAL_CHUNK_DIR))

    if "about niet" in query or query.strip() == "niet":
        return load_chunks_from_dir(OVERVIEW_RESEARCH_DIR)[:top_k]
    
    scored = []

    for chunk in chunks:
        placement = chunk.get("placements", {})
        placement_text = " ".join(str(v) for v in placement.values())

        searchable = normalize(
    " ".join([
        chunk.get("course", ""),
        chunk.get("type", ""),
        chunk.get("event_name",""),
        chunk.get("branch", ""),
        chunk.get("specialization", ""),
        chunk.get("question", ""),
        chunk.get("answer", ""),
        placement_text,
        " ".join(chunk.get("keywords", [])),
    ])
)

        score = 0
        for word in query.split():
            if word in searchable:
                score += 3


        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    if scored:
        return [chunk for _, chunk in scored[:top_k]]

    if source == "admission":
        return load_chunks_from_dir(GENERAL_CHUNK_DIR)[:top_k]

    if source == "overview":
        return load_chunks_from_dir(OVERVIEW_RESEARCH_DIR)[:top_k]

    return chunks[:top_k]

