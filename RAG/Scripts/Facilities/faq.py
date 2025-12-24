import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "index_store" / "faq_data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    FAQS = json.load(f)


def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    replacements = {
        "study": "instruction",
        "language": "instruction",
        "medium": "instruction",
        "niet": ""
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def token_score(a: str, b: str) -> float:
    a_set = set(a.split())
    b_set = set(b.split())
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / len(b_set)


def find_faq(question: str):
    q_norm = normalize(question)

    best = None
    best_score = 0.0

    for faq in FAQS:
        q_list = faq.get("question", [])
        if not q_list:
            continue

        faq_q = normalize(q_list[0])
        score = token_score(q_norm, faq_q)

        if score > best_score:
            best_score = score
            best = faq

    print("BEST SCORE:", best_score)
    return best if best_score >= 0.25 else None

def faq_answer_question(question: str):

    faq = find_faq(question)
    if not faq:
        return "I don't know based on the available information."

    answers = faq.get("answer", [])
    if not answers or not isinstance(answers, list):
        return "I don't know based on the available information."

    return answers[0]


if __name__ == "__main__":
    tests = [
        "hi",
        "medium of study in class in niet",
        "is hostel available?",
        "average package in niet"
    ]

    for q in tests:
        print(f"\nQ: {q}")
        print("A:", faq_answer_question(q))
