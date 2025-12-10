require("dotenv").config();
const express=require("express");
const app=express();
const port=process.env.PORT;
const chatBot=require("./Routes/chatBot_Routes.js");

app.use(express.json());
app.use("/chatBot",chatBot);

app.get("/",(req,res)=>{
    res.status(200).json({msg:"hello world"});
})

app.listen(port,()=>{
    console.log(`server working on ${port}`);
})