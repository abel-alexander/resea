from fastapi import FastAPI, UploadFile, File, Request
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

app = FastAPI()

# Initialize Huggingface QA pipeline for question-answering
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Vectorstore (FAISS)
vectorstore = None

# Huggingface Embedding Model
class HuggingfaceEmbeddings:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Use the mean of the token embeddings for the document embedding
            embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
        return embeddings


# Stage 1: Process the uploaded PDF (PDF Loading, Splitting, Embedding, and Vector Storage)
@app.post("/process_pdf")
async def process_pdf(pdf: UploadFile = File(...)):
    global vectorstore

    # Load the PDF
    loader = PyPDFLoader(pdf.file)
    documents = loader.load()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Generate embeddings using Huggingface model
    hf_embeddings = HuggingfaceEmbeddings()
    doc_embeddings = hf_embeddings.embed_documents([text.page_content for text in texts])

    # Store the vectors in a FAISS vector store
    vectorstore = FAISS.from_documents(documents, hf_embeddings)

    return {"message": "PDF successfully processed!"}


# Stage 2: Handle user QA query (Retrieve relevant chunks and generate response using Huggingface QA model)
@app.post("/ask_question")
async def ask_question(request: Request):
    global vectorstore
    data = await request.json()
    query = data['query']

    # Retrieve relevant documents from the vectorstore
    retrieved_docs = vectorstore.similarity_search(query)

    # Combine the relevant document chunks into a single context
    context = " ".join([doc.page_content for doc in retrieved_docs])

    # Use Huggingface QA pipeline to answer the query based on the context
    answer = qa_pipeline(question=query, context=context)

    return {"answer": answer["answer"]}


# Stage 3: Generate a highlighted PDF (map retrieved chunks to PDF and highlight)
@app.post("/get_highlighted_pdf")
async def get_highlighted_pdf(request: Request):
    global vectorstore
    data = await request.json()
    query = data['query']

    # Retrieve relevant documents from the vectorstore
    retrieved_docs = vectorstore.similarity_search(query)

    # Highlight relevant sections in the original PDF
    highlighted_pdf_url = generate_highlighted_pdf(retrieved_docs)

    return {"pdf_url": highlighted_pdf_url}


# Helper function for generating highlighted PDFs (to be implemented)
def generate_highlighted_pdf(retrieved_docs):
    # Use PyMuPDF or similar library to highlight the relevant sections in the PDF
    pass
