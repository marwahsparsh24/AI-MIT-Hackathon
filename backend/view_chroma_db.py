from chromadb import PersistentClient

PERSIST_DIR = "chroma_db"
client = PersistentClient(path=PERSIST_DIR)

# ✅ List collections
print("✅ Available collections:")
for c in client.list_collections():
    print("-", c)

# ✅ Load the correct collection
collection = client.get_collection(name="contacts")

# ✅ Fetch valid fields only
data = collection.get(include=["documents", "metadatas"])  # removed "ids"

# ✅ Print results
print(f"\n📦 Total Records: {len(data['documents'])}\n")

for i, (doc, meta) in enumerate(zip(data["documents"], data["metadatas"])):
    print(f"--- Contact {i+1} ---")
    print(f"Document: {doc}")
    print(f"Metadata: {meta}\n")