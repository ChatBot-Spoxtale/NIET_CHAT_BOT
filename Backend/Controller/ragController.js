const {translateToEnglish}=require("../RAG/translator");

const ragController={
    translator:async(req,res)=>{
        const {input}=req.body;
        const response=await translateToEnglish(input);
        return res.status(200).json({msg:"successful translate",data:response});
    }
}

module.exports=ragController;