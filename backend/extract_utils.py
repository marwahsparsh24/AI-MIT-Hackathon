import os
import re
import json
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
import base64
import io
from dotenv import load_dotenv
from openai import OpenAI

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is missing. Check your .env file.")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_file_text(tmp_path, suffix, mime_type):
    if mime_type and "pdf" in mime_type:
        doc = fitz.open(tmp_path)
        return "\n".join([page.get_text() for page in doc]), False, ""
    elif mime_type and ("excel" in mime_type or suffix in ["xls", "xlsx"]):
        df = pd.read_excel(tmp_path)
        return df.to_string(), False, ""
    elif mime_type and "image" in mime_type:
        image = Image.open(tmp_path)
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        base64_img = base64.b64encode(buf.getvalue()).decode('utf-8')
        return "", True, base64_img
    else:
        raise ValueError("Unsupported file type")

def call_openai_extraction(prompt, file_text, is_image, base64_img):
    if is_image:
        messages = [
            {"role": "system", "content": "You are a contact parser from event documents and photos."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
            ]}
        ]
        model = "gpt-4o"
    else:
        messages = [
            {"role": "system", "content": "You are a contact parser from structured documents."},
            {"role": "user", "content": f"{prompt}\n\n{file_text}"}
        ]
        model = "gpt-4-turbo"

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```json") or content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    return json.loads(content)
