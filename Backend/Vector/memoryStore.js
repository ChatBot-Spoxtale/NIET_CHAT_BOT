let documents = []; // { id, text, metadata, embedding }

 function addDocument(doc) {
  documents.push(doc);
}

 function setDocuments(docs) {
  documents = docs;
}

 function getDocuments() {
  return documents;
}

function cosineSimilarity(a, b) {
  const dot = a.reduce((sum, v, i) => sum + v * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, v) => sum + v * v, 0));
  const magB = Math.sqrt(b.reduce((sum, v) => sum + v * v, 0));
  return dot / (magA * magB);
}

 function searchSimilar(embedding, topK = 3) {
  return documents
    .map(doc => ({
      ...doc,
      score: cosineSimilarity(embedding, doc.embedding)
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

module.exports={searchSimilar,cosineSimilarity,addDocument,setDocuments,getDocuments};