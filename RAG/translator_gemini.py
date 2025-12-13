import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAS4mie8l2QWf-5xRBVFrO7WFLANQQvE00")

model = genai.GenerativeModel("models/gemini-flash-lite-latest")

# try:
#     models = list(genai.list_models())
#     print("API key works. Available models:\n")
#     for m in models:
#         print(m.name, "-> supports:", m.supported_generation_methods)
# except Exception as e:
#     print("API key error:", e)

TRANSLATE_PROMPT = """
You are a query normalizer for a college admission chatbot.

Rewrite the user query into:
- Clear English
- Formal academic language
- Matching terms used in admission documents

Rules:
- Do NOT answer the question
- Do NOT add new information
- Return only the rewritten query

User query:
"{query}"
"""

def normalize_query(user_query: str) -> str:
    response = model.generate_content(
        TRANSLATE_PROMPT.format(query=user_query),
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 64
        }
    )
    return response.text.strip()


def test_translator():
    test_inputs = [
        "can mca student do mtech?",
        "mba ka admission kaise hota hai",
        "is there quota seat in direct admission",
        "m tech eligibility kya hai",
        "management quota hai kya"
    ]

    for q in test_inputs:
        print("\nOriginal:", q)
        try:
            out = normalize_query(q)
            print("Translated:", out)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    test_translator()
