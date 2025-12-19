import json
import re
import numpy as np
import torch
import faiss
from pathlib import Path
from transformers import BertTokenizer, BertModel
from course_service import handle_user_query
from facilities import facility_answer
from general import general_answer
from overview import overview_answer

# PATHS
ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "index_store"
INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "metadata.json"

# CONFIG 
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256
TOP_K = 8
SCORE_THRESHOLD = 0.60

# LOAD 
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

index = faiss.read_index(str(INDEX_PATH))
metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

def normalize(text: str):
    text = text.lower()
    text = text.replace("&", "and")
    text = text.replace("-", " ")
    text = text.replace(".", "")
    text = text.replace("(", "").replace(")", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

#  COURSE SCHEMA 
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

def alias_match(text: str, alias: str) -> bool:
    return re.search(rf"\b{re.escape(alias)}\b", text) is not None

# INTENT DETECTION 
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


# EMBEDDING
def mean_pooling(output, mask):
    token_embeddings = output.last_hidden_state
    mask = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * mask).sum(1) / mask.sum(1)


def embed_query(text):
    inputs = tokenizer(
        text, truncation=True, padding=True,
        max_length=MAX_LEN, return_tensors="pt"
    )
    with torch.no_grad():
        output = model(**inputs)

    emb = mean_pooling(output, inputs["attention_mask"]).numpy()
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    return emb.astype("float32")


# COURSE PRIORITY
def course_priority(text: str) -> int:
    t = text.lower()
    if "working professional" in t:
        return 0
    if "integrated" in t:
        return 1
    if "regional" in t:
        return 2
    return 3  


# KEYWORD MATCH 
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


# EXTRACTION HELPERS
def extract_duration(text):
    m = re.search(r"duration:\s*([\d]+)\s*year", text, re.I)
    return f"{m.group(1)} years" if m else None


def extract_seats(text):
    m = re.search(r"seats\s*:\s*(\d+)", text, re.I)
    return m.group(1) if m else None


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

def is_reason_query(q):
    return any(k in q for k in ["why", "why choose", "benefit", "benefits", "advantages"])


def is_placement_query(q):
    return any(k in q for k in [
        "placement", "placements", "package",
        "highest", "average", "placement record", "placement stats"
    ])


def is_overview_query(q: str) -> bool:
    q = q.lower()
    return any(
        phrase in q
        for phrase in [
            "tell me about",
            "give details",
            "course details",
            "overview",
            "information about",
            "details of"
        ]
    )


def is_course_chunk(text: str) -> bool:
    return (
        "course name:" in text.lower()
        and "duration:" in text.lower()
    )

# MAIN ANSWER
def answer_question(user_query: str):

    general_keyword = [
        "non veg", "food",
        "bed", "almirah","study table",
        "chair","wifi","ro water",
        "water cooler","geyser","iron",
        "washing clothes","washing machine","laundry"
        ]

    if any(k in user_query.lower() for k in general_keyword):
        return general_answer(user_query) 
    
    facilities = [
        "classroom", "classrooms", "library", "libraries",
        "lab", "labs", "laboratory",
        "medical", "admission",
        "transport", "transportation", "bus", "buses",
        "hostel", "auditorium"
    ]
    if any(k in user_query.lower() for k in facilities):
        return facility_answer(user_query)   

    
    overview_keyword=[
        "award","awards","rankings","ranking","overview","over view","international-alliances",
        "international alliances","research","areas","publications","journals",
        "projects","facilities"
    ]

    if any(k in user_query.lower() for k in overview_keyword):
        return overview_answer(user_query) 


    if any(k in user_query.lower() for k in ["vs", "compare", "difference"]):
        return handle_user_query(user_query)

    user_query_norm = normalize(user_query)
    user_intent = detect_intent(user_query_norm)

    best_match = keyword_course_match(user_query_norm)

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

    if is_overview_query(user_query_norm):

        for item in metadata:
            text = item.get("text", "")

            if not is_course_chunk(text):
                continue

            intent = detect_intent(text)

            if intent["degree"] != user_intent["degree"]:
                continue

            if user_intent["branch"]:
                if intent["branch"] != user_intent["branch"]:
                    continue

            return text.strip()

        return best_match.strip()

    if is_placement_query(user_query_norm):
        return extract_placements(best_match) or "Placements information not available."

    if "duration" in user_query_norm:
        return extract_duration(best_match) or "Duration not available."

    if "seat" in user_query_norm:
        return extract_seats(best_match) or "Seat info not available."

    return best_match.strip()

# CLI 
if __name__ == "__main__":
    while True:
        q = input("\nAsk question (or exit): ").strip()
        if q.lower() == "exit":
            break
        print("\nAnswer:\n", answer_question(q))
