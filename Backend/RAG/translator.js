const { geminiModel } =require("../Config/geminiGenerate.js");

async function translateToEnglish(userQuery) {
  const prompt = `
You are a translator for a college chatbot.
Task: Detect the language and translate the following question to simple English.
Do NOT answer the question. Just return the translated question text.

User query: """${userQuery}"""
`;

  const result = await geminiModel.generateContent(prompt);
  const text = result.response.text().trim();
    console.log(text);

  return text;
}

module.exports={translateToEnglish};