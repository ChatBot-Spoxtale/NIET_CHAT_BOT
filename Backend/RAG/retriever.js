const { embeddingModel } = require("../Config/geminiGenerate.js");
const {searchSimilar}=require("../Vector/memoryStore.js");

async function embedQuery(text) {
  const result = await embeddingModel.embedContent(text);
  return result.embedding.values;
}

 async function retrieveContext(translatedQuery, topK = 3) {
  const queryEmbedding = await embedQuery(translatedQuery);
  const results = searchSimilar(queryEmbedding, topK);

  const context = results.map(r => r.text).join("\n\n---\n\n");
  return context;
}

module.exports={retrieveContext};
