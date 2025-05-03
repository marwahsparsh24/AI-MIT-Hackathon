import os
from uuid import uuid4
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is missing for Chroma embedding.")

# Use PersistentClient instead of in-memory Client
PERSIST_DIR = "chroma_db"  # or any path where you want to store data
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)

# Embedding function using OpenAI
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

# Create or get the persistent collection
collection = chroma_client.get_or_create_collection(
    name="contacts",
    embedding_function=openai_ef
)

# Function to store contacts in ChromaDB
def store_contacts_in_chroma(contacts):
    documents = []
    metadatas = []
    ids = []

    for contact in contacts:
        doc = f"{contact['name']} works at {contact['company']}"
        documents.append(doc)
        metadatas.append(contact)
        ids.append(str(uuid4()))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
