import chromadb

# Create or connect to persistent Chroma collection
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="personal_crm")

def insert_to_chroma(records):
    for idx, record in enumerate(records):
        metadata = {k: v for k, v in record.items() if v is not None}
        collection.add(
            documents=[f"{record['name']} - {record['company']}"],
            metadatas=[metadata],
            ids=[f"id_{record['source_file']}_{idx}"]
        )