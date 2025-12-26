from llm_client import ask_ollama_with_context

SYSTEM_PROMPT = (
    "You are a ChatGPT-style assistant. "
    "Use FAQ for factual replies. Use normal reasoning for general questions."
)

def general_answer(user_query: str) -> str:
    return ask_ollama_with_context(user_query)


def test_context_data():
    questions = [
        # "wifi available?",
        "what is Kathputliyaan club?",
        "list of indoor sports clubs?",
        "hostel rules?",
        # "what is HID club?",
        # "documents required for admission?"
        # "list of clubs",
        # "computer science engineering syllabus link",
        "syllabus for artificial intelligence and machine learning",
        # "btech it syllabus pdf",
        # "vlsi syllabus",
        # "aiml twinning syllabus",
        # "mtech in me",
        # "mtech in cse",
        # "aiml syllabus",
        # "cyber security syllabus"
    ]

    print("\n🧪 TEST RESULTS:\n")
    for q in questions:
        print(f"❓ {q}")
        print(ask_ollama_with_context(q))

if __name__ == "__main__":
    test_context_data()
