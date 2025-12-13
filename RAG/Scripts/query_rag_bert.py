import json
import re
import numpy as np
import torch
import faiss
from pathlib import Path
from transformers import BertTokenizer, BertModel

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from translator_gemini import normalize_query



from translator_gemini import normalize_query

ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "index_store"
INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "metadata.json"

# ---------- CONFIG ----------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256
SCORE_THRESHOLD = 0.75   # confidence filter

# ---------- LOAD ----------
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

# ---------------- Embedding utils ---------------- #

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

# ---------------- Answer cleaning ---------------- #

def clean_answer(text):
    """
    Remove headings and return bullet content only
    """
    lines = text.split("\n")
    bullets = [l.replace("- ", "").strip() for l in lines if l.strip().startswith("-")]

    if bullets:
        return " ".join(bullets)
    return text.strip()

# ---------------- MAIN ---------------- #

def main():
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    while True:
        raw_q = input("\nAsk question (or exit): ")
        if raw_q.lower() == "exit":
            break

        # 🔁 Gemini query normalization
        try:
            normalized_q = normalize_query(raw_q)
            print("🔁 Normalized Query:", normalized_q)
        except Exception as e:
            print("⚠️ Translator failed, using original query")
            normalized_q = raw_q

        # 🔍 Retrieval
        q_emb = embed_query(normalized_q)
        D, I = index.search(q_emb, TOP_K)

        best_score = float(D[0][0])
        best_idx = int(I[0][0])

        print("🔍 Match Score:", round(best_score, 3))

        if best_score < SCORE_THRESHOLD:
            print(" FINAL ANSWER:\nI don't know")
            print("-" * 60)
            continue

        best_text = meta[best_idx]["text"]
        answer = clean_answer(best_text)

        print("FINAL ANSWER:\n")
        print(answer)
        print("-" * 60)

if __name__ == "__main__":
    while True:
        q = input("\nAsk question (or exit): ").strip()
        if q.lower() == "exit":
            break
        print("\nAnswer:", answer_question(q))
