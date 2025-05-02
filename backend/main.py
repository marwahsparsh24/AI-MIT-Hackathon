from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import shutil
from extract_utils import extract_info_from_file
from chroma_utils import insert_to_chroma

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    return {"status": "success", "records_added": len(records)}