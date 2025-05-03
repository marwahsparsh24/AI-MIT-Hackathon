import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- ENVIRONMENT SETUP ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "Missing OPENAI_API_KEY in environment variables"

# --- CHROMA SETUP ---
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("contacts")

# --- EMBEDDING FUNCTION ---
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Reassign collection with embedding support
collection = chroma_client.get_or_create_collection(
    name="contacts", embedding_function=openai_ef
)

# --- CHATBOT FUNCTION ---
import openai

openai.api_key = OPENAI_API_KEY

def fetch_all_records():
    records = collection.get()
    return [
        {
            "name": meta["name"],
            "company": meta["company"],
            "event": meta["event_name"],
            "source": meta["source_file"]
        }
        for meta in records["metadatas"]
    ]

def format_record(record):
    return f"{record['name']} from {record['company']}, met at {record['event']} (Source: {record['source']})"

def get_chatbot_response(user_query: str):
    # Step 1: Search relevant entries
    results = collection.query(query_texts=[user_query], n_results=3)

    if not results["metadatas"] or not results["metadatas"][0]:
        return "Sorry, I couldn’t find any relevant contacts for that."

    suggestions = [format_record(meta) for meta in results["metadatas"][0]]

    # Step 2: Compose reply
    reply = "Here are some contacts that might help:\n\n"
    for s in suggestions:
        reply += f"- {s}\n"
    return reply

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    while True:
        user_input = input("Ask CRM Bot: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = get_chatbot_response(user_input)
        print("\n" + response + "\n")