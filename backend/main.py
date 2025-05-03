from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
import shutil
import mimetypes
import requests
from dotenv import load_dotenv
import os

from openai import OpenAI
from extract_utils import extract_file_text, call_openai_extraction
from models import MessageRequest, SearchRequest
from chroma_utils import store_contacts_in_chroma
from chatbot_utils import run_chatbot

# Load environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise RuntimeError("❌ SERPAPI_KEY is missing. Check your .env file.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Contact Extractor & Message Generator")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔍 LinkedIn profile search using SerpAPI
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

# 📤 Upload & extract endpoint
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
        enriched_contacts = []

        for contact in parsed_contacts:
            name = contact.get("name")
            company = contact.get("company")
            profiles = search_linkedin_profiles(name, company, max_results=3)

            # Add profiles to the contact
            contact["profiles"] = profiles
            enriched_contacts.append(contact)

            results.append({
                "name": name,
                "company": company,
                "profiles": profiles
            })

        # Store enriched contacts in ChromaDB
        store_contacts_in_chroma(enriched_contacts)
        print("✅ Stored enriched contacts in ChromaDB:", enriched_contacts)

        return {"contacts": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

# 🔍 Manual LinkedIn search endpoint
@app.post("/search_linkedin")
def search_linkedin(req: SearchRequest):
    candidates = search_linkedin_profiles(req.name, req.company, req.max_results)
    return {
        "message": "Manual selection recommended. Top 3 candidates returned.",
        "candidates": candidates[:3]
    }

# Health check
@app.get("/")
def root():
    return {"message": "✅ API is running.", "docs": "/docs"}

# 🤖 Chatbot interface
@app.post("/chat")
def chat_with_contacts(request: dict):
    query = request.get("query")
    return {"response": run_chatbot(query)}