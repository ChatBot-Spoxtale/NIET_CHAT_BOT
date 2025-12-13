import os, json
from pathlib import Path
import numpy as np
import torch
import faiss
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

MODEL_NAME = "bert-base-uncased"
TOP_K = 5
MAX_LEN = 256
SCORE_THRESHOLD = 0.75   

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

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


def clean_answer(text):
    lines = text.split("\n")
    bullets = [l.replace("- ", "").strip() for l in lines if l.strip().startswith("-")]

    if bullets:
        return " ".join(bullets)
    return text.strip()


def main():
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    while True:
        raw_q = input("\nAsk question (or exit): ")
        if raw_q.lower() == "exit":
            break
        try:
            normalized_q = normalize_query(raw_q)
        except Exception as e:
            normalized_q = raw_q

        q_emb = embed_query(normalized_q)
        D, I = index.search(q_emb, TOP_K)

        best_score = float(D[0][0])
        best_idx = int(I[0][0])
        if best_score < SCORE_THRESHOLD:
            continue

        best_text = meta[best_idx]["text"]
        answer = clean_answer(best_text)

        print(answer)

if __name__ == "__main__":
    main()
