import os
import json
from uuid import uuid4
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is missing for Chroma embedding.")

# Use persistent client to store data on disk
PERSIST_DIR = "chroma_db"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)

# Set up the OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="contacts",
    embedding_function=openai_ef
)

# Store enriched contact data (with LinkedIn profiles)
def store_contacts_in_chroma(contacts_with_profiles):
    documents = []
    metadatas = []
    ids = []

    for contact in contacts_with_profiles:
        name = contact.get("name")
        company = contact.get("company")
        doc = f"{name} works at {company}"

        # Serialize LinkedIn profiles as a JSON string to comply with ChromaDB
        serialized_profiles = json.dumps(contact.get("profiles", []))

        metadata = {
            "name": name,
            "company": company,
            "profiles": serialized_profiles
        }

        documents.append(doc)
        metadatas.append(metadata)
        ids.append(str(uuid4()))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

# Optional query interface (e.g., for chatbot)
def query_contacts_in_chroma(query_text, top_k=3):
    results = collection.query(query_texts=[query_text], n_results=top_k)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    return list(zip(documents, metadatas))