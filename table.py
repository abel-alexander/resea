import chromadb
from sentence_transformers import SentenceTransformer

# Load ChromaDB Persistent Client
chroma_client = chromadb.PersistentClient(path="./chroma_glossary_db")
collection = chroma_client.get_or_create_collection(name="valuation_framework")
model = SentenceTransformer("all-mpnet-base-v2")

# Load extracted definitions
with open("definition_chunks.json", "r") as f:
    definition_chunks = json.load(f)

# Index chunks in ChromaDB
for i, chunk in enumerate(definition_chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{"category": "valuation"}],
        ids=[f"val_chunk_{i}"]
    )

print("✅ ChromaDB Indexing Complete!")

def retrieve_from_chroma(query, n_results=3):
    """Retrieves relevant chunks from ChromaDB."""
    results = collection.query(query_texts=[query], n_results=n_results)
    return [doc["documents"][0] for doc in results["documents"]] if results["documents"] else []

# Test retrieval
query = "What is DCF valuation?"
chroma_results = retrieve_from_chroma(query)
print("\n🔹 ChromaDB Results:\n", chroma_results)
