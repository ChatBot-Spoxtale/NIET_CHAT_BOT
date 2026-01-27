from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import csv
import os

router = APIRouter()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR,  "callback_requests.csv")


class CallbackRequest(BaseModel):
    name: str
    phone: str


def save_to_csv(name: str, phone: str):
    # Ensure directory exists
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)

    file_exists = os.path.isfile(CSV_FILE_PATH)

    with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header once
        if not file_exists:
            writer.writerow(["Name", "Phone", "Timestamp"])

        writer.writerow([
            name,
            phone,
            datetime.utcnow().isoformat()
        ])


@router.post("/save-callback")
def save_callback(data: CallbackRequest):
    if not data.name.strip() or not data.phone.strip():
        raise HTTPException(status_code=400, detail="Invalid data")

    save_to_csv(data.name, data.phone)
    return {"message": "Callback request saved successfully"}

@router.get("/admin/download-csv")
def download_csv():
    if not os.path.exists(CSV_FILE_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found")

    return {
        "file_path": CSV_FILE_PATH,
        "message": "CSV file is available on the server"
    }