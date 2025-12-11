const { generate } = require("../Config/geminiGenerate.js");
const { translateToEnglish } = require("../RAG/translator.js");
const { generateAnswer } = require("../RAG/answer.js");
const { retrieveContext } = require("../RAG/retriever.js");

const chatBot_Controller = {
    getData: (req, res) => {
        res.status(200).json({ msg: "chatbot" });
    },
    input_msg: async (req, res) => {
        const { input } = req.body;
        try {
            const result = await generate(input);
            res.send({ msg: result });
        } catch (err) {
            console.error(err);
            res.status(500).send({ error: "Internal Server Error", msg: err });
        }
    },
    chatData: async (req, res) => {
        try {
            const { query } = req.body;
            if (!query) {
                return res.status(400).json({ error: "query is required" });
            }

            const translated = await translateToEnglish(query);

            const context = await retrieveContext(translated);

            const answer = await generateAnswer(query, translated, context);

            res.json({
                query,
                translatedQuery: translated,
                answer
            });
        } catch (err) {
            console.error(err);
            res.status(500).json({ error: "Internal server error",data:err });
        }

    }
}

module.exports = chatBot_Controller;