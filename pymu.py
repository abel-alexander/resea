import fitz  # PyMuPDF

# File path to the PDF
file_path = "example.pdf"

# Specify the page range (1-based index)
start_page = 2  # Start from page 2
end_page = 5    # End at page 5 (inclusive)

try:
    # Open the PDF
    pdf_document = fitz.open(file_path)

    # Ensure the range is valid
    if start_page < 1 or end_page > len(pdf_document) or start_page > end_page:
        raise ValueError("Invalid page range specified.")

    # Loop through the specified range
    for page_number in range(start_page - 1, end_page):  # Convert to 0-based index
        # Get the page
        page = pdf_document[page_number]

        # Extract text from the page
        text = page.get_text()

        # Print or process the extracted text
        print(f"\n--- Text from page {page_number + 1} ---\n")
        print(text)

    # Close the document
    pdf_document.close()

except Exception as e:
    print(f"[!] Error: {e}")
