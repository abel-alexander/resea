from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, LlamaForCausalLM
from sentence_transformers import SentenceTransformer
import torch

# Step 1: Load the PDF and Parse it
pdf_path = "path/to/your/pdf/document.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# Step 2: Split the text into chunks for processing
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)

# Step 3: Set up the Embedding Model
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Step 4: Convert the documents to embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Step 5: Store embeddings in a FAISS Vector Store
vectorstore = FAISS.from_documents(split_docs, embeddings)

# Step 6: Set up the LLaMA Model and Tokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")
model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-2-7b", device_map="auto")

# Step 7: Build the RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=model, 
    retriever=vectorstore.as_retriever(), 
    chain_type="stuff", 
    input_tokenizer=tokenizer
)

# Step 8: Ask a Question
question = "Your question here"
response = qa_chain.run(question)
print(response)
