import json
import re
import numpy as np
import torch
import faiss
from pathlib import Path
from transformers import BertTokenizer, BertModel

# ---------- PATHS ----------
ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "index_store"
INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "metadata.json"

# ---------- CONFIG ----------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256
TOP_K = 8
SCORE_THRESHOLD = 0.60

# ---------- LOAD ----------
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

index = faiss.read_index(str(INDEX_PATH))
metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

# ---------- EMBEDDING ----------
def mean_pooling(output, mask):
    token_embeddings = output.last_hidden_state
    mask = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * mask).sum(1) / mask.sum(1)

def embed_query(text):
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=MAX_LEN,
        return_tensors="pt"
    )
    with torch.no_grad():
        output = model(**inputs)

    emb = mean_pooling(output, inputs["attention_mask"]).numpy()
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    return emb.astype("float32")

# ---------- NORMALIZATION ----------
def normalize(text):
    return (
        text.lower()
        .replace("&", "and")
        .replace("-", " ")
        .replace(".", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

# ---------- DEGREE DETECTION ----------
def detect_degree(query):
    q = query.lower()
    if "btech" in q or "b.tech" in q:
        return "b.tech"
    if "mtech" in q or "m.tech" in q:
        return "m.tech"
    if "mba" in q:
        return "mba"
    if "mca" in q:
        return "mca"
    if "bca" in q:
        return "bca"
    if "bba" in q:
        return "bba"
    return None

def extract_duration(text):
    m = re.search(r"duration:\s*([\d]+)\s*year", text, re.I)
    if m:
        return f"{m.group(1)} years"
    return None

def answer_question(user_query: str):
    query_vec = embed_query(user_query)
    D, I = index.search(query_vec, TOP_K)

    degree = detect_degree(user_query)
    q_norm = normalize(user_query)

    best_match = None

    for score, idx in zip(D[0], I[0]):
        if score < SCORE_THRESHOLD:
            continue

        text = metadata[idx]["text"]
        text_lower = text.lower()

        if "working professionals" in text_lower and "working" not in user_query.lower():
            continue
        if "international" in text_lower and "international" not in user_query.lower():
            continue
        if "regional" in text_lower and "regional" not in user_query.lower():
            continue

        if degree and degree not in text_lower:
            continue

        title = text.split("\n")[0]
        if normalize(title) in q_norm or q_norm in normalize(title):
            best_match = text
            break

        if not best_match:
            best_match = text

    if not best_match:
        return "I don't know."

    if "duration" in user_query.lower():
        duration = extract_duration(best_match)
        if duration:
            course = best_match.split("\n")[0].replace("Course Name:", "").strip()
            return f"The duration of {course} is {duration}."
        return "Duration information is not available for this course."

    if "seat" in user_query.lower():
        m = re.search(r"seats:\s*(\d+)", best_match, re.I)
        if m:
            return f"The course has {m.group(1)} seats available."
        return "Seat information is not available."

    if "mode" in user_query.lower():
        m = re.search(r"mode:\s*(.+)", best_match, re.I)
        if m:
            return f"The mode of the course is {m.group(1).strip()}."
        return "Mode information is not available."

    if "facility" in user_query.lower() or "hostel" in user_query.lower():
        return best_match.replace("Facility Name:", "").strip()

    return best_match.strip()

if __name__ == "__main__":
    while True:
        q = input("\nAsk question (or exit): ").strip()
        if q.lower() == "exit":
            break
        print("\nAnswer:", answer_question(q))
