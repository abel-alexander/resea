import fitz  # PyMuPDF
import faiss
import chromadb
import json
import numpy as np
import nltk
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import re

# Initialize NLP components
nltk.download("punkt")
model = SentenceTransformer("all-mpnet-base-v2")

# ==============================
# 🟢 STAGE 1: EXTRACT DATA FROM PDFs
# ==============================

def extract_glossary(pdf_path):
    """Extracts glossary acronyms and their definitions."""
    glossary = {}
    doc = fitz.open(pdf_path)

    for page in doc:
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines:
            match = re.match(r"^([A-Z0-9&/]+)\s*–\s*(.+)$", line.strip())  # Detect "ACRONYM – Definition"
            if match:
                acronym, definition = match.groups()
                glossary[acronym] = definition.strip()

    return glossary

def extract_definition_chunks(pdf_path):
    """Extracts valuation framework text in smaller retrievable chunks."""
    doc = fitz.open(pdf_path)
    chunks = []

    for page in doc:
        text = page.get_text("text").strip()
        sentences = text.split(". ")  # Split into smaller sentence-based chunks

        for i in range(0, len(sentences), 2):  # Group into 2-sentence chunks
            chunk = ". ".join(sentences[i:i+2])
            if len(chunk) > 50:  # Avoid very short lines
                chunks.append(chunk.strip())

    return chunks

# Load PDFs
glossary_pdf_path = "glossary.pdf"
definition_pdf_path = "valuation_framework.pdf"

glossary_data = extract_glossary(glossary_pdf_path)
definition_chunks = extract_definition_chunks(definition_pdf_path)

# Save extracted data
with open("glossary.json", "w") as f:
    json.dump(glossary_data, f, indent=4)

with open("definition_chunks.json", "w") as f:
    json.dump(definition_chunks, f, indent=4)

print("✅ Glossary & Definitions Extracted!")

# ==============================
# 🟢 STAGE 2: INDEXING IN FAISS
# ==============================

# Encode valuation definitions
embeddings = model.encode(definition_chunks)
dimension = embeddings.shape[1]

# Create FAISS index for valuation definitions
val_index = faiss.IndexFlatL2(dimension)
val_index.add(np.array(embeddings, dtype=np.float32))
faiss.write_index(val_index, "faiss_valuation.index")

# Encode glossary terms separately
glossary_acronyms = list(glossary_data.keys())
glossary_definitions = list(glossary_data.values())
glossary_embeddings = model.encode(glossary_definitions)

# Create separate FAISS index for glossary
glossary_index = faiss.IndexFlatL2(glossary_embeddings.shape[1])
glossary_index.add(np.array(glossary_embeddings, dtype=np.float32))
faiss.write_index(glossary_index, "faiss_glossary.index")

# Save term mappings
with open("faiss_glossary_mapping.json", "w") as f:
    json.dump(glossary_definitions, f, indent=4)

with open("faiss_valuation_mapping.json", "w") as f:
    json.dump(definition_chunks, f, indent=4)

print("✅ FAISS Indexing Complete!")

# ==============================
# 🟢 STAGE 3: SETUP HYBRID FAISS + BM25 RETRIEVAL
# ==============================

# Tokenize glossary text for BM25
tokenized_corpus = [nltk.word_tokenize(doc.lower()) for doc in glossary_definitions]
bm25 = BM25Okapi(tokenized_corpus)

def retrieve_from_faiss(query, top_k=3):
    """Retrieves relevant chunks from FAISS (first glossary, then valuation framework)."""
    query_embedding = model.encode([query])

    # Check glossary first
    _, glossary_indices = glossary_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    with open("faiss_glossary_mapping.json", "r") as f:
        stored_glossary = json.load(f)

    glossary_results = [stored_glossary[i] for i in glossary_indices[0] if i < len(stored_glossary)]

    # If glossary has relevant info, return immediately
    if glossary_results:
        return glossary_results

    # Otherwise, check valuation framework
    _, indices = val_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    with open("faiss_valuation_mapping.json", "r") as f:
        stored_definitions = json.load(f)

    return [stored_definitions[i] for i in indices[0] if i < len(stored_definitions)]

def hybrid_search(query, top_k=3):
    """First retrieves from FAISS, then reranks using BM25 for keyword accuracy."""
    faiss_results = retrieve_from_faiss(query, top_k)

    # Apply BM25 ranking if FAISS returns results
    query_tokens = nltk.word_tokenize(query.lower())
    bm25_scores = bm25.get_scores(query_tokens)

    # Get top-ranked glossary definitions
    best_matches = sorted(zip(bm25_scores, glossary_definitions), reverse=True)[:top_k]

    return [match[1] for match in best_matches] + faiss_results

# ==============================
# 🟢 STAGE 4: TEST & BENCHMARK
# ==============================

import time

query = "What is DCF valuation?"

# Measure FAISS retrieval time
start = time.time()
faiss_results = retrieve_from_faiss(query)
faiss_time = time.time() - start

# Measure Hybrid (FAISS + BM25) retrieval time
start = time.time()
hybrid_results = hybrid_search(query)
hybrid_time = time.time() - start

# Print comparison
print("\n🔹 Retrieval Speed Comparison:")
print(f"FAISS Time: {faiss_time:.4f} sec")
print(f"Hybrid FAISS + BM25 Time: {hybrid_time:.4f} sec")

print("\n🔹 Retrieval Accuracy Comparison:")
print(f"FAISS Results:\n{faiss_results}")
print(f"Hybrid Results:\n{hybrid_results}")
