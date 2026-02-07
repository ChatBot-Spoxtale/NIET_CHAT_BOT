
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
import os

router = APIRouter()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "niet_chatbot"
COLLECTION_NAME = "callback_requests"

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment variables")


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


class CallbackRequest(BaseModel):
    name: str
    phone: str


def save_to_db(name: str, phone: str):
    collection.insert_one({
        "name": name.strip(),
        "phone": phone.strip(),
        "timestamp": datetime.utcnow()
    })


@router.post("/save-callback")
def save_callback(data: CallbackRequest):
    if not data.name.strip() or not data.phone.strip():
        raise HTTPException(status_code=400, detail="Invalid data")

    save_to_db(data.name, data.phone)

    return {"message": "Callback request saved successfully"}

@router.get("/admin/callbacks")
def get_callbacks():
    docs = collection.find().sort("timestamp", -1)

    callbacks = [
        {
            "name": d["name"],
            "phone": d["phone"],
            "timestamp": d["timestamp"].isoformat()
        }
        for d in docs
    ]

    return {
        "count": len(callbacks),
        "data": callbacks
    }