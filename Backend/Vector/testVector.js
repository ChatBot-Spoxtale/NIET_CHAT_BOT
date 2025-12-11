const { addDocument, searchSimilar } =require("./memoryStore.js");

function fakeEmbed(text) {
  return text.split("").map(c => c.charCodeAt(0) % 10); 
}

addDocument({
  id: 1,
  text: "Library cards can be made from the admin office.",
  embedding: fakeEmbed("library card admin office")
});

addDocument({
  id: 2,
  text: "Hostel fees must be paid before 15th.",
  embedding: fakeEmbed("hostel fees due date")
});

addDocument({
  id: 3,
  text: "Sports complex is open from 6 AM to 8 PM.",
  embedding: fakeEmbed("sports complex timing")
});

const query = "When can I get a library card?";
const queryEmbedding = fakeEmbed(query);

const results = searchSimilar(queryEmbedding, 2);

console.log("Query:", query);
console.log("Top Results:", results);
