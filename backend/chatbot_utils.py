# chatbot_utils.py
import os
import json
from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI
from chroma_utils import query_contacts_in_chroma

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is missing. Check your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

def run_chatbot(query: str, top_k: int = 3) -> str:
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")

    # Fetch top contact matches from ChromaDB
    top_chunks = query_contacts_in_chroma(query, top_k=top_k)
    if not top_chunks:
        return "Sorry, I couldn't find any relevant contact information."

    context_parts = []

    for doc, meta in top_chunks:
        context = doc

        if meta and "profiles" in meta:
            try:
                profiles = json.loads(meta["profiles"])
                if profiles:
                    profile_lines = "\n".join([
                        f"- Title: {p.get('title', '')}\n  Snippet: {p.get('snippet', '')}\n  Link: {p.get('link', '')}"
                        for p in profiles
                    ])
                    context += f"\n\nEnriched LinkedIn Information:\n{profile_lines}"
            except Exception as e:
                context += f"\n⚠️ Error parsing LinkedIn profiles: {str(e)}"

        context_parts.append(context)

    context_text = "\n\n".join(context_parts)

    # Call OpenAI with full context + guidance
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful CRM assistant. Use the provided contact information and enriched LinkedIn snippets to answer questions about people. This includes their location, education, title, or background."
            },
            {
                "role": "user",
                "content": f"The following contact information may help:\n\n{context_text}\n\nNow answer this:\n{query}"
            }
        ]
    )

    return response.choices[0].message.content
