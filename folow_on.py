# Install necessary packages if not already installed
# !pip install langchain PyPDF2 faiss-cpu transformers torch

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import torch

# Step 1: Set up the Llama 3 8B Instruct Model
device = "cuda" if torch.cuda.is_available() else "cpu"
llm_pipeline = pipeline(
    "text-generation",
    model="llama-3b-instruct",  # Adjust for your 8B version
    device=device
)

llm = HuggingFacePipeline(pipeline=llm_pipeline)

# Step 2: Load and Preprocess Documents
def load_documents(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = text_splitter.split_documents(documents)
    return split_docs

file_path = "path_to_your_pdf.pdf"  # Replace with your PDF file path
documents = load_documents(file_path)

# Step 3: Create Embeddings and Set Up FAISS Index
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
faiss_index = FAISS.from_documents(documents, embeddings)

# Step 4: Set Up the RetrievalQA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=faiss_index.as_retriever(),
    return_source_documents=True
)
# Step 5: Define the Prompt Template and Query the Model
prompt_template = (
    "You are an expert AI model that provides concise, accurate answers based on the following question: "
    "{question}\n\nAnswer:"
)

def ask_question(query):
    # Format the query with the prompt template
    formatted_query = prompt_template.format(question=query)
    result = qa_chain({"query": formatted_query})
    return result

# Example usage: replace with your actual question
query = "What is the main theme of the document?"  # Replace with your question
result = ask_question(query)

# Output answer and source documents
print("Answer:", result["result"])
print("Sources:", [doc.metadata["source"] for doc in result["source_documents"]])
