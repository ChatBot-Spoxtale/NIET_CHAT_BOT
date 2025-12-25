import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import json
import re
import numpy as np
import torch
import faiss

from Scripts.Facilities.compare_course import handle_user_query
from Scripts.Facilities.facilities import facility_answer
from Scripts.Facilities.general import general_answer
from Scripts.Facilities.about_overview import overview_answer
from Scripts.Facilities.admission import admission_answer
from Scripts.Facilities.faq import faq_answer_question
from Scripts.Facilities.overview_course_query import overview_course_query
from Scripts.Facilities.placement_query_rag import query_placement

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "index_store"
INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "metadata.json"

MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256
TOP_K = 8
SCORE_THRESHOLD = 0.60


def get_bert():
    global tokenizer, model
    if tokenizer is None or model is None:
        from transformers import BertTokenizer, BertModel
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        model = BertModel.from_pretrained("bert-base-uncased")
        model.eval()
    return tokenizer, model


index = faiss.read_index(str(INDEX_PATH))
metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

def normalize(text: str):
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[()\-+]", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def is_primary_course_chunk(text: str) -> bool:
    t = text.lower()
    return (
        t.startswith("course name:")
        and "duration:" in t
        and "mode:" in t
    )
COURSE_SCHEMA = {
    "btech mtech": {"aliases": ["btech mtech integrated"]},

    "btech": {
        "aliases": ["btech", "b tech", "b.tech"],
        "branches": {
            "aiml": ["cse aiml", "cse ai ml", "aiml", "ai ml"],
            "ai": ["cse ai", "artificial intelligence", "ai"],
            "ds": ["cse ds", "data science", "ds"],
            "cyber security": ["cse cyber security", "cyber security", "cyber"],
            "iot": ["cse iot", "internet of things", "iot"],
            "csbs": ["csbs"],
            "cse": ["computer science", "cse"],
            "it": ["information technology", "it"],
            "ece": ["electronics", "ece"],
            "me": ["mechanical", "me"],
            "vlsi": ["vlsi"],
            "biotechnology": ["biotechnology", "bio technology"],
        }
    },

    "mtech": {
        "aliases": ["mtech", "m tech", "m.tech"],
        "branches": {
            "ai": ["artificial intelligence", "ai"],
            "cse": ["computer science", "cse"],
            "me": ["mechanical", "me"],
            "ece": ["electronics", "ece"],
            "vlsi": ["vlsi"],
        }
    },

    "bca": {"aliases": ["bca"]},
    "mca": {"aliases": ["mca"]},
    "bba": {"aliases": ["bba"]},
    "mba": {"aliases": ["mba"]},
    "international twinning": {"aliases": ["international twinning"]},
}

def extract_course_name_from_query(query: str) -> str:
    q = normalize(query)

    remove_phrases = [
        "tell me full details about",
        "tell me details about",
        "tell me about",
        "details of",
        "information about",
        "in niet",
        "at niet"
    ]

    for p in remove_phrases:
        q = q.replace(p, "")

    return q.strip()

def alias_match(text: str, alias: str) -> bool:
    return re.search(rf"\b{re.escape(alias)}\b", text) is not None 

def detect_intent(text: str):
    text = normalize(text)
    result = {"degree": None, "branch": None}

    for degree, conf in COURSE_SCHEMA.items():
        if any(alias_match(text, a) for a in conf.get("aliases", [])):
            result["degree"] = degree
            branches = conf.get("branches", {})
            candidates = []

            for branch, aliases in branches.items():
                for a in aliases:
                    candidates.append((branch, a))

            candidates.sort(key=lambda x: len(x[1]), reverse=True)

            for branch, alias in candidates:
                if alias_match(text, alias):
                    result["branch"] = branch
                    return result
            return result

    # branch only
    candidates = []
    for conf in COURSE_SCHEMA.values():
        for branch, aliases in conf.get("branches", {}).items():
            for a in aliases:
                candidates.append((branch, a))

    candidates.sort(key=lambda x: len(x[1]), reverse=True)

    for branch, alias in candidates:
        if alias_match(text, alias):
            result["branch"] = branch
            return result

    return result

def match_course_by_name(course_query: str):
    cq = normalize(course_query)

    best_match = None
    best_score = 0

    for item in metadata:
        text = item.get("text", "")
        if not is_primary_course_chunk(text):
            continue

        course_name = normalize(text.split(":", 1)[1])

        overlap = sum(1 for w in cq.split() if w in course_name)

        if overlap > best_score:
            best_match = text
            best_score = overlap

    return best_match


def mean_pooling(output, mask):
    token_embeddings = output.last_hidden_state
    mask = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * mask).sum(1) / mask.sum(1)

def embed_query(text):
    tokenizer, model = get_bert()
    inputs = tokenizer(text, truncation=True, padding=True,
                       max_length=MAX_LEN, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs)

    emb = mean_pooling(output, inputs["attention_mask"]).numpy()
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    return emb.astype("float32")
last_matched_course = None


def is_placement_query(q):
    return any(k in q for k in [
        "placement", "placements", "package",
        "highest", "average", "placement record", "placement stats"
    ])

def extract_duration(course_block):
    m = re.search(r"Duration:\s*([\w\s]+)", course_block)
    return f" Duration: {m.group(1)}" if m else None


def extract_seats(course_block):
    m = re.search(r"Seats:\s*([\d]+)", course_block)
    return f" Seats: {m.group(1)}" if m else None


def course_priority(text: str) -> int:
    t = text.lower()
    if "working professional" in t:
        return 0
    if "integrated" in t:
        return 1
    if "regional" in t:
        return 2
    return 3  


def keyword_course_match(user_query):
    q = normalize(user_query)
    user_intent = detect_intent(q)

    best_score = -1
    best_priority = -1
    best_text = None

    for item in metadata:
        text = item.get("text", "")
        if not text:
            continue

        nt = normalize(text)
        item_intent = detect_intent(text)

        if user_intent["degree"] and item_intent["degree"]:
            if user_intent["degree"] != item_intent["degree"]:
                continue

        if user_intent["branch"]:
            if item_intent["branch"]:
                if user_intent["branch"] != item_intent["branch"]:
                    continue
            else:
                if user_intent["branch"] not in nt:
                    continue

        score = sum(1 for w in q.split() if w in nt)
        priority = course_priority(text)

        if score > best_score or (score == best_score and priority > best_priority):
            best_score = score
            best_priority = priority
            best_text = text

    return best_text


def extract_placements(text):
    m = re.search(r"Placements\s*:\s*(\{.*?\})", text, re.I)
    if not m:
        return None
    try:
        data = eval(m.group(1))
        return (
            f"Placements Offered: {data.get('placements_offered', 'N/A')}\n"
            f"Highest Package: {data.get('highest_package', 'N/A')}\n"
            f"Average Package: {data.get('average_package', 'N/A')}"
        )
    except:
        return None

last_matched_course = None

def answer_question(user_query: str):
    global last_matched_course

    q = user_query.lower().strip()

    # greeting_keyword = [
    #     "hi","hii","hey","namaste","good morning",
    #     "good afternoon","good evening","good night",
    #     "good night","hello","how are you","how was day"
    #     ]
    # if any(k in q for k in greeting_keyword):
    #     return ask_ollama(user_query)
    
    detected_course = match_course_by_name(q)
    if detected_course:
        last_matched_course = detected_course  # store memory
        return detected_course
    
    if last_matched_course:
        if "seat" in q or "seats" in q:
            seats = extract_seats(last_matched_course)
            return seats or "Seat info not available."

        if "duration" in q:
            duration = extract_duration(last_matched_course)
            return duration or "Duration info not available."

        if is_placement_query(q):
            placement = query_placement(last_matched_course)
            return placement or "Placement info not available."
  
    
    if any(k in q for k in ["vs", "compare", "difference"]):
        return handle_user_query(user_query)
    overview_course_keywords = [
        "detail", "overview", "what","details","choose","about"
    ]
    if any(k in q for k in overview_course_keywords):
        return overview_course_query(user_query)

    #------placement record------
    placement_record_keywords = [
        "placement", "highest package", "placement details"
    ]
    if any(k in q for k in placement_record_keywords):
        return query_placement(user_query)
    # ---------------- 2️⃣ ADMISSION ----------------
    admission_keywords = [
        "admission", "apply", "eligibility",
        "jee", "direct", "counselling",
        "lateral entry", "documents",
        "fees", "fee structure"
    ]
    if any(k in q for k in admission_keywords):
        return admission_answer(user_query)

    # ---------------- 3️⃣ GENERAL ----------------
    general_keyword = [
        "non veg", "food",
        "bed", "almirah","study table",
        "chair","wifi","ro water",
        "water cooler","geyser","iron",
        "tea","coffee","chai",
        "washing clothes","washing machine","laundry"
        ]
    if any(k in q for k in general_keyword):
        return general_answer(user_query)

    course_query = extract_course_name_from_query(user_query)
    # course_match = match_course_by_name(course_query)

    # if course_match:
    #     last_matched_course = course_match  
    #     return course_match.strip()


    overview_keywords = [
        "about niet", "about the college",
        "overview of niet",
        "award", "awards",
        "ranking", "rankings",
        "nirf",
        "research",
        "publications", "journals",
        "projects",
        "infrastructure",
        "facilities"
    ]

    if any(k in q for k in overview_keywords):
        return overview_answer(user_query)

    # ---------------- FACILITIES ----------------
    facilities = [
        "classroom", "classrooms", "library", "libraries",
        "lab", "labs", "laboratory",
        "medical", 
        "transport", "transportation", "bus", "buses",
        "hostel", "auditorium"
    ]
    if any(k in user_query.lower() for k in facilities):
        return facility_answer(user_query)
        # return generate_answer(context, user_query)

    faq = [
        "study", "instruction", "language", "medium",
         "autonomous", "visitors",
        "medium of study", "Housing","accommodation",
        "timings","education loan","scholarship",
        "eligible","deposit","documents",
        "transport", "average package ", "agents", "consultant",
        "hostel", "admission"
    ]
    if any(k in user_query.lower() for k in faq):
        return faq_answer_question(user_query)


    user_query_norm = normalize(user_query)
    user_intent = detect_intent(user_query_norm)
    course_query = extract_course_name_from_query(user_query)

    best_match = keyword_course_match(user_query_norm)
    if best_match:
        last_matched_course = best_match  
        return best_match
    

    if not best_match:
        q_vec = embed_query(user_query_norm)
        D, I = index.search(q_vec, TOP_K)

        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(metadata):
                continue
            if score < SCORE_THRESHOLD:
                continue

            text = metadata[idx]["text"]
            intent = detect_intent(text)

            if user_intent["degree"] and intent["degree"]:
                if user_intent["degree"] != intent["degree"]:
                    continue

            best_match = text
            break

    if not best_match:
        return "Sorry, I couldn't find relevant course information."

    if len(course_query.split()) >= 3:
        q_vec = embed_query(normalize(course_query))
        D, I = index.search(q_vec, TOP_K)

        for score, idx in zip(D[0], I[0]):
            if score < SCORE_THRESHOLD:
                continue

            text = metadata[idx]["text"]
            if is_primary_course_chunk(text):
                return text.strip()
            
   


def demo_rag_llm():
    tests = [
        # "Tell me full details about B. Tech CSE (Cyber-Security) in NIET",
        #  "medium of study in class in niet",
        # "is hostel available?",
        # "average package in niet",
                # "what is btech cse",
                "hi"

    ]

    print("\n" + "=" * 80)
    print("FINAL COURSE MATCHING TEST")
    print("=" * 80)

    for q in tests:
        print("\nQ:", q)
        print("A:", answer_question(q))

if __name__ == "__main__":
    demo_rag_llm()
