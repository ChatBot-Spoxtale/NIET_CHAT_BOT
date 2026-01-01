import json
import re
import os

INPUT_FILE  = "metadata.json"           
OUTPUT_FILE = "metadata_cleaned.json"   


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    text = text.strip()

    text = re.sub(r"(?i)(what is|who is|tell me about)[\s\S]*?\?", "", text).strip()

    text = re.sub(r"^[\/\\\-\|]+", "", text).strip()

    text = re.sub(r"\s+", " ", text).strip()

    if text and text[-1] not in ".!?":
        text += "."

    return text


def clean_entry(entry: dict) -> dict:
    """Clean each record (question, answer, etc.)"""

    for key in ["question", "answer", "department", "club_name"]:
        if key in entry and isinstance(entry[key], str):
            entry[key] = clean_text(entry[key])

    if "question" in entry and "answer" in entry:
        if entry["question"].lower() in entry["answer"].lower():
            entry["answer"] = entry["answer"].replace(entry["question"], "").strip()

    return entry


def clean_metadata():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found in this directory.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = [clean_entry(item) for item in data]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4, ensure_ascii=False)

    print("Metadata Cleaned Successfully!")
    print(f" Input : {INPUT_FILE}")
    print(f" Output: {OUTPUT_FILE}")
    print(f" Total Records Cleaned: {len(cleaned)}")


if __name__ == "__main__":
    clean_metadata()
