import os
import chromadb
from chromadb.utils import embedding_functions
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is missing for Chroma embedding.")

chroma_client = chromadb.Client()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"  # or any supported model
)

collection = chroma_client.get_or_create_collection(
    name="contacts",
    embedding_function=openai_ef
)

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
