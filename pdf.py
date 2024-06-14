import fitz  # Import PyMuPDF

def extract_text_by_bookmarks(pdf_path, bookmarks):
    doc = fitz.open(pdf_path)
    text_outputs = {bookmark: "" for bookmark in bookmarks}  # Initialize text storage for each bookmark
    
    for bookmark in bookmarks:
        # Attempt to find the bookmark; skip if not found
        try:
            # Get the location of the bookmark (page number)
            page = doc.find_bookmark(bookmark)
            page_text = doc[page].get_text("text")
            text_outputs[bookmark] += page_text
        except ValueError:
            print(f"Bookmark '{bookmark}' not found in {pdf_path}.")
    
    doc.close()
    return text_outputs

# Define PDF files and the bookmarks you are interested in
pdf_files = ["pib1.pdf", "pib2.pdf"]
bookmarks = ["Equity Research", "News"]  # These should match the exact bookmark names in the PDFs

# Process each file
for pdf in pdf_files:
    extracted_texts = extract_text_by_bookmarks(pdf, bookmarks)
    for section, text in extracted_texts.items():
        filename = f"{pdf.replace('.pdf', '')}_{section}.txt"
        with open(filename, "w") as f:
            f.write(text)
            print(f"Extracted {section} from {pdf} to {filename}")
