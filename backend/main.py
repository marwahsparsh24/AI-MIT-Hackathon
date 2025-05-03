<<<<<<< HEAD
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
=======
from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
>>>>>>> origin/Sparsh
import shutil
import mimetypes
import requests
from dotenv import load_dotenv
import os
from extract_utils import extract_file_text, call_openai_extraction
from models import MessageRequest, SearchRequest
from chroma_utils import store_contacts_in_chroma

<<<<<<< HEAD
from extract_utils import extract_info_from_file
from chroma_utils import insert_to_chroma
=======
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise RuntimeError("❌ SERPAPI_KEY is missing. Check your .env file.")
>>>>>>> origin/Sparsh

app = FastAPI(title="LinkedIn Contact Extractor & Message Generator")

<<<<<<< HEAD
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
=======
def search_linkedin_profiles(name, company, max_results=5):
    query = f'"{name}" {company} site:linkedin.com/in/'
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": max_results,
        "filter": 0
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"SerpAPI error: {response.text}")
    results = response.json().get("organic_results", [])
    return [
        {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
        for r in results if r.get("link") and "/in/" in r.get("link")
    ]

@app.post("/search_linkedin")
def search_linkedin(req: SearchRequest):
    candidates = search_linkedin_profiles(req.name, req.company, req.max_results)
    return {"message": "Manual selection recommended. Top 3 candidates returned.", "candidates": candidates[:3]}

@app.post("/upload_and_extract")
async def upload_and_extract(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1]
    with NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    mime_type, _ = mimetypes.guess_type(tmp_path)
    try:
        file_text, is_image, base64_img = extract_file_text(tmp_path, suffix, mime_type)

        prompt = """
You are an AI assistant. Extract people from the document with:
- name
- company
- title (optional)
Return ONLY a JSON array. No explanation, no markdown, no commentary.
"""
        parsed_contacts = call_openai_extraction(prompt, file_text, is_image, base64_img)

        results = []
        for contact in parsed_contacts:
            name = contact.get("name")
            company = contact.get("company")
            profiles = search_linkedin_profiles(name, company, max_results=3)
            results.append({"name": name, "company": company, "profiles": profiles})

        # ✅ Store in ChromaDB
        store_contacts_in_chroma(parsed_contacts)
        print("✅ Stored contacts in ChromaDB:", parsed_contacts)

        return {"contacts": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

@app.get("/")
def root():
    return {"message": "✅ API is running.", "docs": "/docs"}
>>>>>>> origin/Sparsh
