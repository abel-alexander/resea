import os
import fitz  # Import PyMuPDF as fitz

def extract_text_by_bookmarks(pdf_path, bookmarks):
    doc = fitz.open(pdf_path)
    text_outputs = {bookmark: "" for bookmark in bookmarks}  # Initialize text storage for each bookmark
    
    toc = doc.get_toc()  # Table of contents (list of bookmarks)
    bookmark_pages = {entry[1]: entry[2] - 1 for entry in toc if entry[1] in bookmarks}  # Get pages for our bookmarks
    
    for bookmark, start_page in bookmark_pages.items():
        text = []
        end_page = next((page for bm, page in bookmark_pages.items() if page > start_page), len(doc))
        
        for page_num in range(start_page, end_page):
            page = doc[page_num]
            text.append(page.get_text("text"))
        
        text_outputs[bookmark] = "\n".join(text)
    
    doc.close()
    return text_outputs

# Specify the path to your folder containing PDF files
folder_path = '/path/to/your/folder'

# List all PDF files in the folder
files = os.listdir(folder_path)
pdf_files = [file for file in files if file.lower().endswith('.pdf')]

# Define the bookmarks you are interested in
bookmarks = ["Equity Research", "News"]  # Adjust these to match the exact bookmarks in your PDFs

# Process each PDF file
for pdf in pdf_files:
    pdf_path = os.path.join(folder_path, pdf)  # Full path to the PDF file
    extracted_texts = extract_text_by_bookmarks(pdf_path, bookmarks)
    for section, text in extracted_texts.items():
        filename = f"{pdf.replace('.pdf', '')}_{section}.txt"
        with open(os.path.join(folder_path, filename), "w") as f:  # Save to the same folder or specify another
            f.write(text)
            print(f"Extracted {section} from {pdf} to {filename}")
