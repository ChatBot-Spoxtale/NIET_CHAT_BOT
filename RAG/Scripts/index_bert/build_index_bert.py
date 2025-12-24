import json
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


def normalize_course_name(name: str):
    n = name.lower()

    degree = ""
    if "b.tech" in n or "btech" in n:
        degree = "BTech"
    elif "m.tech" in n or "mtech" in n:
        degree = "MTech"
    elif "mba" in n:
        degree = "MBA"
    elif "mca" in n:
        degree = "MCA"
    elif "bca" in n:
        degree = "BCA"
    elif "bba" in n:
        degree = "BBA"

    branches = []
    if "artificial intelligence" in n or "aiml" in n:
        branches += ["AIML", "AI", "Artificial Intelligence"]
    if "data science" in n:
        branches += ["Data Science", "DS"]
    if "cyber" in n:
        branches += ["Cyber Security"]
    if "computer science" in n or "cse" in n:
        branches += ["Computer Science", "CSE"]
    if "information technology" in n or "it" in n:
        branches += ["Information Technology", "IT"]
    if "electronics" in n or "ece" in n:
        branches += ["Electronics", "ECE"]
    if "mechanical" in n or "me" in n:
        branches += ["Mechanical Engineering", "ME"]
    if "biotechnology" in n:
        branches += ["Biotechnology"]

    return degree, branches


def build_chunks(data):
    chunks = []

    courses = data.get("courses", {})

    for course_id, course in courses.items():
        if not isinstance(course, dict):
            continue

        name = course.get("course_name", "")
        duration = course.get("duration", "")
        seats = course.get("seats", "")
        mode = course.get("mode", "")
        why = course.get("why_choose", "")
        url = course.get("source_url", "")

        degree, branches = normalize_course_name(name)

        name_l = name.lower()
        is_twinning = "twinning" in name_l
        is_working = "working professional" in name_l or "working professionals" in name_l

        chunks.append({
            "text": f"""
Course Name: {name}
Degree: {degree}
Branches: {", ".join(branches)}
Duration: {duration}
Seats: {seats}
Mode: {mode}
Source URL: {url}
            """.strip(),
            "meta": {
                "type": "course",
                "degree": degree,
                "branches": branches,
                "twinning": is_twinning,
                "working_professional": is_working
            }
        })

        if isinstance(why, str) and why.strip():
            chunks.append({
                "text": f"Why choose {name}: {why}",
                "meta": {
                    "type": "why_choose",
                    "course": name
                }
            })

        chunks.append({
            "text": f"""
{name} is also known as:
{degree} {" ".join(branches)}
{"twinning program" if is_twinning else ""}
            """.strip(),
            "meta": {
                "type": "alias",
                "course": name
            }
        })

    facilities = data.get("facilities", {})

    for facility_type, fac_list in facilities.items():
        if not isinstance(fac_list, list):
            continue

        category_name = facility_type.replace("_", " ").title()

        for fac in fac_list:
            if not isinstance(fac, dict):
                continue

            fname = fac.get("name", category_name)
            summaries = fac.get("summary", [])
            source = fac.get("source_url", "")

            if isinstance(summaries, list):
                for s in summaries:
                    if not s.strip():
                        continue

                    chunks.append({
                        "text": f"""
Facility: {fname}
Category: {category_name}
Description: {s}
Source URL: {source}
                        """.strip(),
                        "meta": {
                            "type": "facility",
                            "category": category_name
                        }
                    })

            elif isinstance(summaries, str) and summaries.strip():
                chunks.append({
                    "text": f"""
Facility: {fname}
Category: {category_name}
Description: {summaries}
Source URL: {source}
                    """.strip(),
                    "meta": {
                        "type": "facility",
                        "category": category_name
                    }
                })
    return chunks


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = build_chunks(data)

    dim = 768
    index = faiss.IndexFlatIP(dim)
    metadata = []

    for i, chunk in enumerate(tqdm(chunks)):
        vec = embed_text(chunk["text"])
        index.add(np.array([vec]))
        metadata.append({
        "id": f"chunk_{i}",
        "text": chunk["text"],
        "meta": chunk.get("meta", {})
    })

    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"FAISS index built successfully")
    print(f" Total chunks indexed: {len(metadata)}")


if __name__ == "__main__":
    main()

