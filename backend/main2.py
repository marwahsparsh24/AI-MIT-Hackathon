from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
import shutil
import mimetypes
import requests
import os
import time
from dotenv import load_dotenv

from openai import OpenAI

# Project modules
from extract_utils import extract_file_text, call_openai_extraction
from models import MessageRequest, SearchRequest, SendRequest
from chroma_utils import store_contacts_in_chroma
from chatbot_utils import run_chatbot
from linkedIn_bot import connect_with_message  # From main2.py

# Load environment variables
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SERPAPI_KEY or not OPENAI_API_KEY:
    raise RuntimeError("❌ Required environment variables missing.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn CRM Assistant",
    description="Upload contacts, extract data, search LinkedIn profiles, generate messages, and send connection requests."
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task status tracking
tasks = {}

# 🔍 LinkedIn profile search
def search_linkedin_profiles(name, company, max_results=3):
    query = f'"{name}" {company} site:linkedin.com/in/'
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": max_results,
        "filter": 0
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        profiles = []
        for r in results:
            link = r.get("link", "")
            if "/in/" in link:
                title = r.get("title", "").replace(" | LinkedIn", "").strip()
                snippet = r.get("snippet", "").lower()
                position = ""
                if " at " in snippet:
                    try:
                        part = snippet.split(" at ")[0].strip()
                        if len(part) < 50:
                            position = part.capitalize()
                    except:
                        pass
                profiles.append({
                    "name": title,
                    "link": link,
                    "snippet": r.get("snippet", ""),
                    "position": position
                })
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")

# 🖋️ Message generator
def generate_message(sender_name, recipient_name, recipient_company, position, context):
    position_info = f"Position: {position}" if position else ""
    prompt = f"""
You are a helpful assistant writing a personalized LinkedIn connection message.

Sender: {sender_name}
Recipient: {recipient_name}
Recipient Company: {recipient_company}
{position_info}
Context: {context}

Write a short, friendly, and professional message that:
- Mentions the context naturally
- Expresses interest in connecting
- Is personalized to the recipient
- Feels human-written and conversational
- Can be pasted directly into LinkedIn's connect box

Important: Keep the message under 300 characters as LinkedIn has a strict character limit.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant writing great LinkedIn messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        message = response.choices[0].message.content.strip()
        if len(message) > 300:
            message = message[:297] + "..."
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation error: {e}")

# 🔁 Background task for LinkedIn automation
async def send_connection_request_task(task_id, profile_url, message):
    try:
        tasks[task_id] = {"status": "running", "message": "Connecting..."}
        result = await connect_with_message(profile_url, message)
        tasks[task_id] = {"status": "completed", "message": result}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "message": str(e)}

# 📤 Upload & extract contacts
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
        enriched_contacts = []

        for contact in parsed_contacts:
            name = contact.get("name")
            company = contact.get("company")
            profiles = search_linkedin_profiles(name, company, max_results=3)
            contact["profiles"] = profiles
            enriched_contacts.append(contact)

        store_contacts_in_chroma(enriched_contacts)
        return {"contacts": enriched_contacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

# 🧠 Chatbot query
@app.post("/chat")
def chat_with_contacts(request: dict):
    query = request.get("query")
    return {"response": run_chatbot(query)}

# 🔍 Manual LinkedIn search
@app.post("/search_linkedin")
def manual_search(req: SearchRequest):
    profiles = search_linkedin_profiles(req.name, req.company, req.max_results)
    return {
        "message": "Top profiles returned.",
        "candidates": profiles[:3]
    }

# 🔄 Search & generate message
@app.post("/search_and_generate")
def search_and_generate(req: SearchRequest):
    profiles = search_linkedin_profiles(req.name, req.company)
    if not profiles:
        return {"message": "No profiles found.", "candidates": []}
    first_profile = profiles[0]
    position = first_profile.get("position", "")
    message = generate_message(
        sender_name=req.sender_name,
        recipient_name=req.name,
        recipient_company=req.company,
        position=position,
        context=req.context
    )
    return {"candidates": profiles, "custom_message": message}

# ✉️ Send connection request
@app.post("/send_request")
async def send_linkedin_request(req: SendRequest, background_tasks: BackgroundTasks):
    task_id = f"task_{int(time.time())}"
    tasks[task_id] = {"status": "pending", "message": "Task scheduled"}
    background_tasks.add_task(send_connection_request_task, task_id, req.profile_url, req.message)
    return {"task_id": task_id, "status": "pending", "message": "Request initiated"}

# ⏱️ Task status
@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# ✅ Health check
@app.get("/")
def root():
    return {
        "message": "✅ LinkedIn CRM Assistant is running",
        "docs": "/docs"
    }
