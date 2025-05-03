from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import shutil

from extract_utils import extract_info_from_file
from chroma_utils import insert_to_chroma

app = FastAPI()

# Allow CORS for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== File Upload Route ==========
@app.post("/add-file")
async def add_file(file: UploadFile = File(...), event_name: Optional[str] = Form(None)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted = extract_info_from_file(file_path, file.filename)
    os.remove(file_path)

    records = []
    for entry in extracted:
        record = {
            "name": entry.get("name"),
            "company": entry.get("company"),
            "source_file": file.filename,
            "event_name": event_name,
        }
        records.append(record)

    insert_to_chroma(records)
    return {"status": "success", "records_added": len(records), "records": records}

# ========== Manual Entry Route ==========
@app.post("/add-manual")
async def add_manual(request: Request):
    body = await request.json()
    print("🚀 Incoming Manual Data:", body)

    required_fields = ["name", "company", "event_name"]
    for field in required_fields:
        if field not in body:
            return {"error": f"Missing field: {field}"}

    record = {
        "name": body.get("name"),
        "company": body.get("company"),
        "event_name": body.get("event_name"),
        "source_file": body.get("source_file", "manual-entry")
    }

    insert_to_chroma([record])
    return {"status": "success", "records_added": 1, "records": [record]}