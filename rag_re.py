import gradio as gr
import PyPDF2
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    full_text = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        full_text.append((page_num, text))
    return full_text

# Function to find sentences with keywords
def find_sentences_with_keywords(pdf_file, keywords):
    if not pdf_file:
        return "No file uploaded"
    
    full_text = extract_text_from_pdf(pdf_file)
    keywords = keywords.split(",")  # Support for multiple keywords
    found_sentences = []
    
    for page_num, (page_index, text) in enumerate(full_text):
        sentences = re.split(r'(?<=[.!?]) +', text)  # Split into sentences
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                # Add sentence with reference to the page number
                found_sentences.append(f"{sentence} [Page {page_index + 1}]")
    
    return "\n\n".join(found_sentences)

# Gradio interface
def pdf_keyword_search(pdf_file, keywords):
    # Find sentences based on keywords
    results = find_sentences_with_keywords(pdf_file, keywords)
    
    # Return results (with keyword matches highlighted on the PDF as a future step)
    return results

def display_pdf_page(pdf_file, page_number):
    # Here you can add logic to render the specific page of the PDF.
    # For simplicity, we'll assume PyPDF2 can be used to display text of a single page.
    if pdf_file is None:
        return "No file uploaded."
    
    full_text = extract_text_from_pdf(pdf_file)
    for page_num, (page_index, text) in enumerate(full_text):
        if page_index == page_number - 1:
            return text
    return "Page not found."

# Build Gradio app
with gr.Blocks() as demo:
    gr.Markdown("# PDF Keyword Search Tool")
    
    # File uploader
    pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
    
    # User input for keywords
    keyword_input = gr.Textbox(label="Enter keywords (comma separated)", placeholder="e.g. data, science")
    
    # Chat box interface (left side)
    with gr.Row():
        with gr.Column():
            output_box = gr.Textbox(label="Search Results", placeholder="Sentences with keywords will appear here.", interactive=False, lines=10)
            submit_button = gr.Button("Submit")
        
        # Display PDF on the right side
        with gr.Column():
            pdf_display = gr.Textbox(label="Highlighted PDF content", interactive=False, lines=30)
    
    # Logic for submission
    submit_button.click(pdf_keyword_search, inputs=[pdf_file, keyword_input], outputs=output_box)
    
    # Logic to display content based on the page reference
    output_box.change(display_pdf_page, inputs=[pdf_file, output_box], outputs=pdf_display)

# Launch the app
demo.launch()
