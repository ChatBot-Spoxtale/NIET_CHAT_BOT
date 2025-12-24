# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM

# MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"

# print("Loading tokenizer...")
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# print("Loading model (CPU mode)...")
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     torch_dtype=torch.float32,     
#     device_map="cpu",              
#     low_cpu_mem_usage=True
# )

# model.eval()
# print("LLM loaded successfully")


# def generate_answer(context: str, question: str) -> str:
#     context = context[:2000]

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a factual college assistant. "
#                 "Use ONLY the information provided in the context. "
#                 "Give a short, clear, human-readable answer. "
#                 "Do NOT repeat the question. "
#                 "Do NOT explain reasoning. "
#                 "If the answer is not in the context, reply exactly: "
#                 "'I don't know based on the available information.'"
#             )
#         },
#         {
#             "role": "system",
#             "content": f"Context:\n{context}"
#         },
#         {
#             "role": "user",
#             "content": question
#         }
#     ]

#     # Build prompt
#     prompt = tokenizer.apply_chat_template(
#         messages,
#         tokenize=False,
#         add_generation_prompt=True
#     )

#     inputs = tokenizer(
#         prompt,
#         return_tensors="pt",
#         truncation=True,
#         max_length=1024          
#     )

#     input_len = inputs["input_ids"].shape[1]

#     with torch.no_grad():
#         output = model.generate(
#             **inputs,
#             max_new_tokens=50,     
#             do_sample=False,
#             repetition_penalty=1.1
#         )

#     generated_tokens = output[0][input_len:]
#     response = tokenizer.decode(
#         generated_tokens,
#         skip_special_tokens=True
#     ).strip()

#     if "." in response:
#         response = response.split(".")[0].strip() + "."

#     return response


# if __name__ == "__main__":
#     test_context = "BTech AIML has a total intake capacity of 240 seats."
#     test_question = "How many seats are available in BTech AIML?"

#     print("\n--- TEST OUTPUT ---")
#     print(generate_answer(test_context, test_question))


import ollama

def generate_answer(context, question):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly, polite college chatbot. "
                "If the user greets you (hi, hello, namaste), "
                "reply warmly like ChatGPT. "
                "Use short, natural sentences. "
                "You may use emojis politely."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = ollama.chat(
        model="gemma3:1b",
        messages=messages,
        options={
            "temperature": 0.4,
            "num_predict": 60
        }
    )

    return response["message"]["content"].strip()



# Test
ctx = "BTech AIML has a total intake capacity of 240 seats."
q = "How many seats are available in BTech AIML?"

# print(generate_answer(ctx, q))
