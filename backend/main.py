from fastapi import FastAPI, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile
import shutil
import mimetypes
import requests
from dotenv import load_dotenv
import os
from extract_utils import extract_file_text, call_openai_extraction
from models import MessageRequest, SearchRequest
from chroma_utils import store_contacts_in_chroma

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise RuntimeError("❌ SERPAPI_KEY is missing. Check your .env file.")

app = FastAPI(title="LinkedIn Contact Extractor & Message Generator")

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