# rag/llm/gemini_client.py

import os
from dotenv import load_dotenv # type: ignore
from google import genai
from openai import OpenAI # type: ignore
load_dotenv()

TEST_MODE = True        
MAX_TEST_WORDS = 30

#gemini 
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

#open AI
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
MODEL = "models/gemini-2.0-flash-lite"

def is_detailed_query(question: str) -> bool:
    q = question.lower()
    return any(phrase in q for phrase in [
        "more detail",
        "more details",
        "in detail",
        "full detail",
        "full details",
        "full summary",
        "explain more",
        "elaborate",
        "tell me more",
        "complete information"
    ])

def build_prompt(context: str, question: str, history: list) -> str:
    history_text = "\n".join(
        f"{h['role']}: {h['content']}" for h in history
    )

    return f"""
You are a friendly, professional admission counsellor and assistant for NIET.

TONE & STYLE:
- Be warm, clear, and human-like (not robotic).
- Explain things as you would to a student or parent.
- Be confident but honest.
- Do NOT sound like a marketing brochure.
- Do NOT use emojis.

BEHAVIOR RULES:
- If the user's message is a greeting or casual conversation
  (hello, hi, thanks, how are you, bye),
  respond naturally and politely like a human assistant.

- For "why choose / why should I take admission / should I join" questions:
  • Give a direct answer in 3–5 bullet points
  • Do NOT add long introductions
  • Keep the response under 80 words

- If the question is about NIET (admission, courses, facilities, clubs, research, events):
  - Answer ONLY using the information provided below.
  - Rephrase and summarize the information in a helpful, conversational way.
  - For “why choose / is it good / should I take admission” questions,
    respond like a counsellor explaining benefits clearly and calmly.

- If the user asks about autonomy, autonomous status, recognition, affiliation,
  approval, or degree validity:
  • Clearly explain what autonomy means,
  • Explain why it is beneficial for students,
  • Reassure that the degree remains valid and follows regulatory
    and affiliation guidelines,
  • Use ONLY the provided NIET information (do not invent approvals).

If the user asks a comparison question (e.g. "better than", "vs", "instead of", "compare"):
- Identify all relevant courses mentioned
- Use only the provided course information
- Compare them in a balanced, counsellor-style explanation
- Do NOT repeat only one course overview
- Do NOT claim one course is universally better
- Explain which type of student each course is suitable for

- Do NOT use external knowledge or assumptions.
- If the required NIET information is NOT present in the context,
  reply exactly with:
  "Please Visit Our Website For More Informations :- https://www.niet.co.in/"
ANSWER LENGTH CONTROL (VERY IMPORTANT):


- By default:
  • Answer in STRICTLY no more than 20 words
    OR at most 2 short sentences.
  • Be precise and informative.
  • Do NOT add examples or background.

- ONLY if the user clearly asks for:
  "more details", "full summary", "in detail", "explain more", or similar:
  • Then provide a full, detailed explanation
  • Use paragraphs or bullet points if helpful

If the user asks about arrests, bans, closures, fraud, legal issues, or rumors related to NIET:
- Do NOT answer the question
- Do NOT speculate
- Politely redirect to official channels
- Provide only the official website URL

Conversation History:
{history_text}

Available Information (use only this):
{context}

User Question:
{question}

Final Answer (human, clear, and helpful):
"""

def generate_answer(context: str, question: str, history: list):
    prompt = build_prompt(context, question, history)
    detailed = is_detailed_query(question)

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-lite",
            contents=prompt
        )

        answer = response.text.strip()
        
        if not detailed:
            answer = " ".join(answer.split()[:20])
        return answer

    except Exception as gemini_error:
        # error_text = str(gemini_error).lower()
        print("Gemini failed:", gemini_error)

        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful NIET admission assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            answer = completion.choices[0].message.content.strip()

            if TEST_MODE:
                answer = " ".join(answer.split()[:MAX_TEST_WORDS])

            return answer

        except Exception as openai_error:
            print("OpenAI also failed:", openai_error)

            return (
                "Our system is currently experiencing high traffic. "
                "Please try again in a few minutes or visit our website: "
                "https://www.niet.co.in/"
            )
