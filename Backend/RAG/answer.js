const { geminiModel } =require("../Config/geminiGenerate.js");

 async function generateAnswer(userQuery, translatedQuery, context) {
  const prompt = `
You are an assistant for NIET (Noida Institute of Engineering and Technology).
Answer the student's question based ONLY on the context below.
If the answer is not in the context, say you don't have that specific information.

User original question:
"${userQuery}"

Translated question:
"${translatedQuery}"

Context:
"""${context}"""

Now give a clear, friendly, concise answer.
  `;

  const result = await geminiModel.generateContent(prompt);
  return result.response.text().trim();
}

module.exports={generateAnswer};

