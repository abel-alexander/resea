import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embeddings model
model = SentenceTransformer("all-mpnet-base-v2")

# Load extracted definitions
with open("definition_chunks.json", "r") as f:
    definition_chunks = json.load(f)

# Encode definitions into vectors
embeddings = model.encode(definition_chunks)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype=np.float32))

# Save FAISS index
faiss.write_index(index, "faiss_glossary.index")
with open("faiss_mapping.json", "w") as f:
    json.dump(definition_chunks, f, indent=4)

print("✅ FAISS Indexing Complete!")

def retrieve_from_faiss(query, top_k=3):
    """Retrieves relevant chunks from FAISS."""
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)
    
    with open("faiss_mapping.json", "r") as f:
        stored_definitions = json.load(f)
    
    return [stored_definitions[i] for i in indices[0] if i < len(stored_definitions)]

# Test retrieval
faiss_results = retrieve_from_faiss(query)
print("\n🔹 FAISS Results:\n", faiss_results)
