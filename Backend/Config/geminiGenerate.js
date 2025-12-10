// Config/geminiGenerate.js
const { GoogleGenerativeAI } = require("@google/generative-ai");
require("dotenv").config();

const apiKey = process.env.API_KEY;

if (!apiKey) {
    console.error("Missing API_KEY in .env");
}

const genAI = new GoogleGenerativeAI(apiKey);

const geminiModel = 
    genAI.getGenerativeModel({
        model: "gemini-flash-latest",
    });


const generate = async (prompt) => {
    try {
        console.log("Prompt to Gemini:", prompt);

        const result = await geminiModel.generateContent(prompt);
        const response = result.response;
        const text = response.text();

        console.log("AI Response:", text);
        return text;
    } catch (err) {
        console.error("Error generating content:", err);
        return "Failed to generate content";
    }
};

module.exports = { generate, geminiModel };
