import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]
KB = BASE / "index_store" / "overview_data.json"

def norm(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    synonyms = {
        "awards": "award",
        "award": "award",

        "rankings": "ranking",
        "ranking": "ranking",
        "rank": "ranking",
        "ranked": "ranking",

        "committees": "committee",
        "committee": "committee",

        "student life": "student_life",
        "student-life": "student_life",

        "project":"projects",
        "porject":"projects",

        "publication":"publications",
        "journal":"journals"
    }

    for k, v in synonyms.items():
        text = text.replace(k, v)

    return text.strip()


def tokenize(text: str):
    return set(norm(text).split())

def match_score(a: str, b: str) -> int:
    return len(tokenize(a) & tokenize(b))

def load():
    with open(KB, encoding="utf-8") as f:
        data=json.load(f)
    return build_general_chunks(data)

def extract_field(text, field):
    pattern = rf"{field}\s*:\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def build_general_chunks(data):
    chunks = []
    cid = 1

    institute = data.get("institute", {})
    for section, items in institute.items():
        if isinstance(items, list):
            chunks.append({
                "id": str(cid),
                "category": "Institute",
                "topic": section.replace("_", " ").title(),
                "text": " ".join(items)
            })
            cid += 1

    research = data.get("research", {})
    for section, items in research.items():

        if isinstance(items, list) and all(isinstance(i, str) for i in items):
            chunks.append({
                "id": str(cid),
                "category": "Research",
                "topic": section.replace("_", " ").title(),
                "text": " ".join(items)
            })
            cid += 1

        if section == "projects":
            for row in items:
                chunks.append({
                    "id": str(cid),
                    "category": "Research Project",
                    "topic": row[1],
                    "text": f"PI: {row[2]}. {row[3]}. Year: {row[4]}"
                })
                cid += 1

    facilities = data.get("facilities", [])
    chunks.append({
        "id": str(cid),
        "category": "Facilities",
        "topic": "Campus Facilities",
        "text": " ".join(facilities)
    })

    return chunks

def parse_general_chunk(chunk):
    if not isinstance(chunk, dict):
        return None

    required_keys = {"id", "category", "topic", "text"}
    if not required_keys.issubset(chunk.keys()):
        return None

    return {
        "id": str(chunk.get("id")),
        "category": str(chunk.get("category", "")),
        "topic": str(chunk.get("topic", "")),
        "text": str(chunk.get("text", ""))
    }

def find_general(chunks, query):
    best = None
    best_score = 0

    q_norm = norm(query)
    q_tokens = tokenize(q_norm)

    for chunk in chunks:
        parsed = parse_general_chunk(chunk)
        if not parsed:
            continue

        topic = norm(parsed["topic"])
        category = norm(parsed["category"])
        text = norm(parsed["text"])

        haystack = f"{category} {topic} {text}"

        score = match_score(q_norm, haystack)

        if any(t in topic for t in q_tokens):
            score += 3

        if any(t in category for t in q_tokens):
            score += 2

        if score > best_score:
            best_score = score
            best = parsed

    return best if best_score >= 1 else None


def overview_answer(user_query: str):
    chunks = load()
    result = find_general(chunks, user_query)

    if not result:
        return "Sorry, I could not find information about this facility."
    return (
        f" {result['text']}"
    )
    

def demo_from_real_dataset():
    queries = [
        # "tell me about niet institute",
        # "what rankings does niet have",
        # "research areas in ai",
        # "biotechnology research projects",
        # "what facilities are available at niet",
        # "who received project grant in 2024",
        "tell me about research projects",
        "publications ",
        "facilities"
    ]

    for q in queries:
        print("=" * 70)
        print("QUERY:", q)

        result = overview_answer(q)

        if result:
            # print("CATEGORY:", result["category"])
            # print("TOPIC   :", result["topic"])
            print( result,"...")
        else:
            print("NO MATCH FOUND")


if __name__ == "__main__":
   demo_from_real_dataset()
#    print(general_answer("hostel and transport"))
    