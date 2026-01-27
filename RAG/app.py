# main.py

from llm_model_gemini.chat import chat

print("NIET Course RAG Bot (type 'exit')\n")

while True:
    q = input("You: ")
    if q.lower() == "exit":
        break

    print("\nBot:", chat(q), "\n")
