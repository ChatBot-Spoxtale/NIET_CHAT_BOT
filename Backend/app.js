require("dotenv").config();
const express=require("express");
const app=express();
const port=process.env.PORT;
const chatBot=require("./Routes/chatBot_Routes.js");
const ragRoutes=require("./Routes/ragRoutes.js");

app.use(express.json());
app.use("/chatBot",chatBot);
app.use("/rag",ragRoutes);

app.get("/",(req,res)=>{
    res.status(200).json({msg:"hello world"});
})

app.listen(port,()=>{
    console.log(`server working on ${port}`);
})