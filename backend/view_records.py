import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="personal_crm")

results = collection.get()
print(f"📦 Total Records: {len(results['ids'])}\n")

for meta in results["metadatas"]:
    name = meta.get("name", "[no name]")
    company = meta.get("company", "[no company]")
    event = meta.get("event_name", "[no event]")

    print(f"- {name} @ {company} (Event: {event})")