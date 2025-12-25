import json, os

BASE_DIR = os.path.dirname(__file__)

SOURCE_PATH = os.path.join(BASE_DIR,"..", "..", "data", "urls_data.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "..","..", "index_store", "url_chunks.json")

def create_syllabus_chunks():
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    pdf_links = data.get("pdfs", [])
    chunks = []

    for pdf in pdf_links:
        course_name = (
            pdf.split("/")[-1]
            .replace(".pdf","")
            .replace("-", " ")
            .replace("_"," ")
            .lower()
        )

        chunks.append({
            "course": course_name,
            "type": "syllabus",
            "syllabus_url": pdf
        })

    # Save chunks
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        json.dump(chunks, out, indent=4)

    print("\n🎯 SUCCESS! Syllabus chunks created.")
    print("📄 Source:", SOURCE_PATH)
    print("➡ Saved to:", OUTPUT_PATH, "\n")


if __name__ == "__main__":
    create_syllabus_chunks()
