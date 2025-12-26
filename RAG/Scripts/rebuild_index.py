import json, numpy as np, faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "index_store/metadata.json"
INDEX_PATH = ROOT / "index_store/faiss_index.bin"

metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = []
for item in metadata:
    text = item.get("text", "")
    emb = model.encode(text)
    embeddings.append(emb)

embeddings = np.array(embeddings).astype("float32")

dim = embeddings.shape[1]  # Should be 384
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

faiss.write_index(index, str(INDEX_PATH))

print(f"New FAISS index created with dimension {dim}.")
