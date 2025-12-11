const { GoogleGenerativeAI } = require("@google/generative-ai");
const { embeddingModel } =require("../Config/geminiGenerate.js"); // your embedding model file
const { addDocument, searchSimilar } =require("./memoryStore.js");

async function test() {
  const model = embeddingModel;

  function embed(text) {
    return model.embedContent({ content: text }).then(res => res.embedding.values);
  }

  addDocument({
    id: 1,
    text: "Library card made from admin office.",
    embedding: await embed("library card admin office")
  });

  const queryEmbedding = await embed("How to get library card?");
  const results = searchSimilar(queryEmbedding, 3);

  console.log(results);
}

test();
