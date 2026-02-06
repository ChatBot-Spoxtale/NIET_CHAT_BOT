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


@router.get("/admin/callbacks")
def get_callbacks():
    if not os.path.exists(CSV_FILE_PATH):
        return {
            "count": 0,
            "data": []
        }

    callbacks = []

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if not row or not row.get("Name"):
                continue

            callbacks.append({
                "name": row["Name"].strip(),
                "phone": row["Phone"].strip(),
                "timestamp": row["Timestamp"].strip()
            })

    return {
        "count": len(callbacks),
        "data": callbacks
    }