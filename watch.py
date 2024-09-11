import gradio as gr
import requests

# API Endpoints
API_BASE_URL = "http://127.0.0.1:8000"  # Replace with your FastAPI base URL

# Function to handle the PDF upload (Stage 1)
def upload_pdf(pdf):
    pdf_file = pdf.name
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()

    # Send the PDF to the backend API for processing
    response = requests.post(f"{API_BASE_URL}/process_pdf", files={"pdf": pdf_bytes})
    
    if response.status_code == 200:
        return "PDF successfully processed!"
    else:
        return f"Failed to process PDF: {response.text}"

# Function to handle the QA query (Stage 2)
def ask_question(query):
    # Send the query to the backend API
    response = requests.post(f"{API_BASE_URL}/ask_question", json={"query": query})
    
    if response.status_code == 200:
        return response.json()["answer"]
    else:
        return f"Failed to get an answer: {response.text}"

# Function to retrieve the highlighted PDF (Stage 3)
def get_highlighted_pdf(query):
    # Send the query to the backend API to get the highlighted PDF
    response = requests.post(f"{API_BASE_URL}/get_highlighted_pdf", json={"query": query})
    
    if response.status_code == 200:
        return response.json().get("pdf_url", "Could not generate highlighted PDF")
    else:
        return f"Failed to get highlighted PDF: {response.text}"

# Gradio interface for the three stages
with gr.Blocks() as demo:
    gr.Markdown("## Stage 1: Upload PDF")
    pdf_input = gr.File(label="Upload your PDF")
    upload_button = gr.Button("Upload and Process PDF")
    upload_output = gr.Textbox(label="Output")

    upload_button.click(upload_pdf, inputs=pdf_input, outputs=upload_output)

    gr.Markdown("## Stage 2: Ask a Question")
    query_input = gr.Textbox(label="Enter your query")
    ask_button = gr.Button("Ask Question")
    answer_output = gr.Textbox(label="Answer")

    ask_button.click(ask_question, inputs=query_input, outputs=answer_output)

    gr.Markdown("## Stage 3: Get Highlighted PDF")
    query_input_2 = gr.Textbox(label="Enter your query (for PDF highlighting)")
    highlight_button = gr.Button("Get Highlighted PDF")
    highlight_output = gr.Textbox(label="Highlighted PDF URL")

    highlight_button.click(get_highlighted_pdf, inputs=query_input_2, outputs=highlight_output)

# Launch Gradio app
demo.launch()
