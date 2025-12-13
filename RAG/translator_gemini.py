import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-lite-latest")

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
