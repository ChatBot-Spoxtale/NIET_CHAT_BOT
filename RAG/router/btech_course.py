# btech_router.py

import json, os, re

# 📁 Load B.Tech data file
BTECH_PATH = os.path.join(os.path.dirname(__file__), "../data/btech_chunks.json")
with open(BTECH_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

BTECH_DATA = data if isinstance(data, list) else [data]

# 🔧 Normalize function for safe matching
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[.\-]', ' ', text)  # b.tech → b tech
    return " ".join(text.split())


# 🎯 Main Router Function
def btech_router(query: str):
    q = normalize(query)

    # Not a B.Tech query → pass to other routers
    if "btech" not in q and "b tech" not in q and "b.tech" not in q:
        return None

    # Try matching branch based on keywords
    for course in BTECH_DATA:

        # 🎯 Match course keywords
        if any(keyword in q for keyword in course["keywords"]):

    # 1️⃣ SPECIFIC ANSWERS FIRST
            if "seat" in q or "seats" in q:
                return f"🎓 **Seats:** {course['properties'].get('seats', 'Not available')}"

            if "duration" in q or "year" in q:
                return f"⏳ **Duration:** {course['properties'].get('duration', 'Not available')}"

            if "eligibility" in q or "criteria" in q:
                return f"📝 **Eligibility:** {course['properties'].get('eligibility', 'Not available')}"

            if "fee" in q or "fees" in q:
                return f"💸 **Fees:** {course['properties'].get('fees','Check admission department')}"

            if "placement" in q or "package" in q:
                p = course.get("placements", {})
                return f"""
💼 **Placement - {course['course']}**
• Average: {p.get('average','NA')}
• Highest: {p.get('highest','NA')}
• Recruiters: {", ".join(p.get('recruiters',[])) or "NA"}
""".strip()
        # 🌟 Why Choose / Benefits Handling
        if any(word in q for word in ["why choose","why this","benefit","advantage","kyu","kyun","kyo"]):
            why = course.get("why_choose", [])
            if why:
                return "🌟 **Why Choose this Course?**\n- " + "\n- ".join(why)
            else:
                return "This course offers strong learning, placement, and future career scope."

        if any(word in q for word in ["overview","about","detail","tell me","kaisa","kya hai"]):
            return course.get("overview", "No overview available.")


# 🧪 ----------------------------------------------------
# 🧪 TEST FUNCTION (Run this file directly to test)
# 🧪 ----------------------------------------------------
def test_btech_router():
    test_queries = [
        "about btech aiml",
        " Overview B.Tech-CSE (Artificial Intelligence)",
        "btech cse aiml placement",
        "what is the duration of btech cse aiml",
        "what is the duration of btech cse ai",
        "placement record of btech cse ds",
        "why choose this btech cse ai"
    ]

    print("\n🔍 Running B.Tech Router Test Cases:\n")
    for q in test_queries:
        print(f"❓ Query: {q}")
        print(f"👉 Response: {btech_router(q)}\n")


# Run test if file executed directly
if __name__ == "__main__":
    test_btech_router()
