# FILE: RAG/build_vectors.py

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  
META_OUTPUT = os.path.join(BASE_DIR, "metadata_cleaned.json")
VEC_OUTPUT = os.path.join(BASE_DIR, "vectors.npy")
FAISS_OUTPUT = os.path.join(BASE_DIR, "vector_store.faiss")


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
print(f"📌 Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)


def load_all_chunks():
    all_chunks = []
    print("\n Reading chunk files from:", DATA_DIR)

    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            path = os.path.join(DATA_DIR, file)
            print(f"   ➝ Found: {file}")

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_chunks.extend(data)

    print(f"\nTotal Chunks Loaded: {len(all_chunks)}")
    return all_chunks



def build_vector_store():
    chunks = load_all_chunks()

    if not chunks:
        print(" No JSON chunk files found in /data. Add chunk files first!")
        return

    texts = [item["answer"] for item in chunks]

    print("\nGenerating Embeddings (this may take time)...")
    vectors = model.encode(texts)
    vectors = np.array(vectors).astype("float32")

    print(" Saving metadata & vectors...")
    np.save(VEC_OUTPUT, vectors)

    with open(META_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, FAISS_OUTPUT)

    print("\n VECTOR STORE BUILT SUCCESSFULLY!")
    print("Files Generated:")
    print(f"   - {FAISS_OUTPUT}")
    print(f"   - {VEC_OUTPUT}")
    print(f"   - {META_OUTPUT}")
    print("\n RAG is ready to use!")



if __name__ == "__main__":
    print("🚀 STARTING VECTOR BUILD PROCESS...")
    build_vector_store()
