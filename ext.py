from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

# Step 1: Load Markdown File
loader = UnstructuredMarkdownLoader("input.md")
docs = loader.load()

# Step 2: Chunk Text
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# Step 3: Embed Text
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = FAISS.from_documents(chunks, embedding_model)

# Step 4: Create a RAG Chain
retriever = vector_store.as_retriever()
llm = HuggingFacePipeline.from_model_id(model_id="meta-llama/Llama-3-8B-Instruct")

rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

# Step 5: Ask a Question
query = "What is the main topic discussed in the markdown file?"
response = rag_chain.run(query)
print(response)
