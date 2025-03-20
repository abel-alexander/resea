import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB and embedding model
chroma_client = chromadb.PersistentClient(path="./definition_knowledgebase")
collection = chroma_client.get_or_create_collection(name="valuation_framework")
model = SentenceTransformer("all-mpnet-base-v2")

def extract_definition_chunks(pdf_path):
    """Extracts valuation framework text in smaller retrievable chunks."""
    import fitz
    doc = fitz.open(pdf_path)
    chunks = []

    for page in doc:
        text = page.get_text("text").strip()
        paragraphs = text.split("\n\n")  # Split by paragraphs

        for para in paragraphs:
            if len(para) > 100:  # Avoid very short lines
                chunks.append(para.strip())

    return chunks

# Extract and index definitions
definition_pdf_path = "valuation_framework.pdf"
definition_chunks = extract_definition_chunks(definition_pdf_path)

# Store chunks in ChromaDB
for i, chunk in enumerate(definition_chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{"category": "valuation"}],
        ids=[f"val_chunk_{i}"]
    )

print("✅ Definition file indexed in ChromaDB!")
