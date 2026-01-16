from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import csv
import os

router = APIRouter()

CSV_FILE_PATH = "RAG/callback_requests.csv"

class CallbackRequest(BaseModel):
    name: str
    phone: str


def save_to_csv(name: str, phone: str):
    file_exists = os.path.isfile(CSV_FILE_PATH)

    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

    with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Name", "Phone", "Timestamp"])

        writer.writerow([
            name,
            phone,
            datetime.utcnow().isoformat()
        ])


@router.post("/save-callback")
def save_callback(data: CallbackRequest):
    if not data.name or not data.phone:
        raise HTTPException(status_code=400, detail="Invalid data")

    save_to_csv(data.name, data.phone)

    return {"message": "Saved to CSV successfully"}


@router.get("/admin/download-csv")
def download_csv():
    if not os.path.exists(CSV_FILE_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found")

    return {
        "file": CSV_FILE_PATH

    }
