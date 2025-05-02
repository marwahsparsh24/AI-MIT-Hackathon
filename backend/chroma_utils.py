import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid

# ChromaDB setup
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))
collection = client.get_or_create_collection(name="contacts")

# Sentence transformer model for embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def insert_to_chroma(metadata: dict):
    document = build_document(metadata)
    embedding = embedder.encode(document).tolist()
    record_id = str(uuid.uuid4())

    collection.add(
        ids=[record_id],
        documents=[document],
        embeddings=[embedding],
        metadatas=[metadata]
    )
    return record_id

def build_document(metadata):
    # Concatenate available fields for semantic embedding
    parts = [metadata.get(field) for field in ['name', 'designation', 'company', 'email', 'phone', 'misc_info']]
    return " | ".join(filter(None, parts))