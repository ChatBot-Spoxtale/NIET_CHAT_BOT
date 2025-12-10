const { generate } = require("../Config/geminiGenerate.js");

const chatBot_Controller = {
    getData: (req, res) => {
        res.status(200).json({ msg: "chatbot" });
    },
    input_msg: async (req, res) => {
        const {input} = req.body;
        try {
            const result = await generate(input);
            res.send({ msg: result });
        } catch (err) {
            console.error(err);
            res.status(500).send({ error: "Internal Server Error", msg: err });
        }
    }
}

module.exports = chatBot_Controller;