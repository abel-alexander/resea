
# Required Libraries
from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.rerankers import MonoT5Reranker, DistilBERTReReranker

# Step 1: Load PDF and Extract Content as a Document Object
def load_pdf_as_document(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    metadata = reader.metadata
    for page in reader.pages:
        text += page.extract_text()
    return Document(page_content=text, metadata={"source": pdf_path, "metadata": metadata})

# Step 2: Split the Text into Chunks
def split_text(document):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(document.page_content)
    return chunks

# Step 3: Embedding Using all-mpnet-base-v2
def get_embeddings(chunks):
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    embeddings = [embedder.embed(chunk) for chunk in chunks]
    return embeddings

# Step 4: Store in Chroma for Retrieval
def store_in_chroma(chunks, embedder):
    chroma_store = Chroma.from_texts(chunks, embedder)
    return chroma_store

# Step 5: Retrieval (BM25, Hybrid Search, HyDE)
def retrieve_with_hybrid_search(query, chroma_db, chunks):
    from langchain.retrievers import BM25Retriever, HybridRetriever
    bm25_retriever = BM25Retriever.from_documents(chunks)
    hybrid_retriever = HybridRetriever(retrievers=[bm25_retriever, chroma_db.as_retriever()])
    retrieved_docs = hybrid_retriever.get_relevant_documents(query)
    return retrieved_docs

# Step 6: Reranking with monoT5 or DistilBERT
def rerank_documents(reranker, docs):
    reranked_docs = reranker.rerank(docs)
    return reranked_docs

# Step 7: Query with Citations Using Custom LLM (Hugging Face)
def query_with_custom_llm(query, chroma_db, llm):
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=chroma_db.as_retriever())
    answer_with_sources = qa_chain({"query": query}, return_docs=True)
    final_answer = answer_with_sources['result']
    return final_answer, answer_with_sources['source_documents']

# Step 8: Repacking (Reverse)
def reverse_repacking(docs):
    return docs[::-1]

# Step 9: Summarization (Extractive and Abstractive)
def extractive_summary(docs):
    return docs  # Placeholder for actual BM25-based extractive summary

def abstractive_summary(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# Example pipeline with optional summarization
def run_pipeline(pdf_path, query, use_summarization=False):
    # Step 1: Load PDF
    document = load_pdf_as_document(pdf_path)
    
    # Step 2: Split text into chunks
    chunks = split_text(document)
    
    # Step 3: Embedding the chunks
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    embeddings = get_embeddings(chunks)
    
    # Step 4: Store in Chroma
    chroma_db = store_in_chroma(chunks, embedder)
    
    # Step 5: Retrieve documents with hybrid search
    retrieved_docs = retrieve_with_hybrid_search(query, chroma_db, chunks)
    
    # Step 6: Rerank the documents (optional, using monoT5 or DistilBERT)
    reranker = MonoT5Reranker(model_name="castorini/monot5-base-msmarco")  # Use DistilBERT if needed
    reranked_docs = rerank_documents(reranker, retrieved_docs)
    
    # Step 7: Query and return final answer with citations using custom LLM
    hf_pipeline = pipeline("text-generation", model="gpt2")
    llm = HuggingFacePipeline(pipeline=hf_pipeline)
    final_answer, sources = query_with_custom_llm(query, chroma_db, llm)
    
    # Step 8: Optional summarization
    if use_summarization:
        # Summarization (both extractive and abstractive)
        summary = extractive_summary(reranked_docs)  # Example for extractive
        abstractive_summ = abstractive_summary(reranked_docs[0].page_content)  # Example for abstractive
    else:
        summary = "Summarization skipped"
        abstractive_summ = "Summarization skipped"
    
    # Step 9: Repack the documents (Reverse)
    repacked_docs = reverse_repacking(reranked_docs)
    
    return final_answer, summary, abstractive_summ

# Example usage
pdf_path = "path_to_your_pdf.pdf"
query = "What is the main argument in the document?"
final_answer, summary, abstractive_summ = run_pipeline(pdf_path, query, use_summarization=True)

print("Final Answer:", final_answer)
print("Extractive Summary:", summary)
print("Abstractive Summary:", abstractive_summ)
