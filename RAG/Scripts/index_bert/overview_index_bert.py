import json
import re
import torch
import faiss
import numpy as np
from pathlib import Path
from transformers import BertTokenizer, BertModel

# -------------------------
# CONFIG
# -------------------------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 256

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "overview_course_data.json"
INDEX_DIR = ROOT / "index_store"
INDEX_PATH = INDEX_DIR / "faiss_index.bin"
META_PATH = INDEX_DIR / "overview_metadata.json"

INDEX_DIR.mkdir(exist_ok=True)

# -------------------------
# Normalization
# -------------------------
def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------
# Mean Pooling
# -------------------------
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )

# -------------------------
# Load Model
# -------------------------
print("🔄 Loading BERT model...")
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertModel.from_pretrained(MODEL_NAME)
model.eval()

# -------------------------
# Load Data
# -------------------------
print("📄 Loading course data...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []
metadata = []

for slug, item in data.items():
    text = normalize(item["summary"])
    documents.append(text)
    metadata.append({
        "course_slug": slug,
        "text": item["summary"]
    })

# -------------------------
# Create Embeddings
# -------------------------
print("🧠 Creating embeddings...")
embeddings = []

with torch.no_grad():
    for doc in documents:
        inputs = tokenizer(
            doc,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=MAX_LEN
        )
        output = model(**inputs)
        emb = mean_pooling(output, inputs["attention_mask"])
        embeddings.append(emb.cpu().numpy())

embeddings = np.vstack(embeddings).astype("float32")

# -------------------------
# Build FAISS Index
# -------------------------
print("📦 Building FAISS index...")
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
faiss.normalize_L2(embeddings)
index.add(embeddings)

# -------------------------
# Save Index & Metadata
# -------------------------
faiss.write_index(index, str(INDEX_PATH))

with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("✅ Index built successfully!")
print(f"📌 Total documents indexed: {len(metadata)}")
