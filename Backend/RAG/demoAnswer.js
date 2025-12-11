const { generateAnswer } =require("../RAG/answer.js");

(async () => {
  const userQuery = "Hostel timing kya hai?";
  const translatedQuery = "What are the hostel timings?";
  
  const context = `
Hostel closes at 10 PM and opens at 6 AM.
Mess facility is available for students.
`;

  const finalAnswer = await generateAnswer(userQuery, translatedQuery, context);
  console.log("BOT ANSWER:\n", finalAnswer);
})();
