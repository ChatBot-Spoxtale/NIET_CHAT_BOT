import os, json
from pathlib import Path
import numpy as np
import torch
import faiss
from transformers import BertTokenizer, BertModel
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "base_knowledge.json"
INDEX_DIR = ROOT / "index_store"
INDEX_DIR.mkdir(exist_ok=True)

INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "metadata.json"

MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

# ---------------- Embedding utils ---------------- #

def mean_pooling(output, mask):
    token_embeddings = output.last_hidden_state
    mask = mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return (token_embeddings * mask).sum(1) / mask.sum(1)

def embed_text(text: str):
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
    return emb[0].astype("float32")

# ---------------- SMART CHUNKING ---------------- #

def build_chunks(data):
    chunks = []

    # ---- COURSES ----
    courses = data.get("courses", {})
    for course_id, course in courses.items():
        block = f"""
        Course Name: {course.get("course_name", "")}
        Duration: {course.get("duration", "")}
        Mode: {course.get("mode", "")}
        Seats: {course.get("seats", "")}
        """
        chunks.append(block.strip())

    # ---- FACILITIES ----
    facilities = data.get("facilities", {})
    for fac_id, fac in facilities.items():
        block = f"""
        Facility Name: {fac.get("facility_name", "")}
        Summary: {fac.get("summary", "")}
        Features:
        """
        for feat in fac.get("features", []):
            block += f"- {feat}\n"

        chunks.append(block.strip())

    return chunks


# ---------------- MAIN ---------------- #

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = build_chunks(data)

    print(f"✅ Built {len(chunks)} semantic chunks")

    dim = 768
    index = faiss.IndexFlatIP(dim)
    metadata = []

    for i, chunk in enumerate(tqdm(chunks)):
        vec = embed_text(chunk)
        index.add(np.array([vec]))
        metadata.append({
            "id": f"chunk_{i}",
            "text": chunk
        })

    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("🎉 BERT FAISS index built with high-quality chunks")

if __name__ == "__main__":
    main()
