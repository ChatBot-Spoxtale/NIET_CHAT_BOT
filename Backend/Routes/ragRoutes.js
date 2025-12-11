const express=require("express");
const router=express.Router();
const ragController=require("../Controller/ragController");

router.post("/transalate",ragController.translator);

module.exports=router;