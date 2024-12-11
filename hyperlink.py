import fitz  # PyMuPDF

# Load the PDF
pdf_path = "your_document.pdf"
doc = fitz.open(pdf_path)

# Analyze the first page (assuming it contains the ToC)
toc_page_number = 0  # Zero-indexed
page = doc[toc_page_number]

# Extract links
links = page.get_links()

# Iterate over links and resolve their destinations
for i, link in enumerate(links):
    if 'page' in link:  # Direct page link
        destination_page = link['page']
        print(f"Link {i+1} points to page {destination_page + 1} (1-indexed).")
    elif 'uri' in link:  # External URL
        uri = link['uri']
        print(f"Link {i+1} points to external URL: {uri}")
    else:
        print(f"Link {i+1} has an unknown or unsupported type: {link}")

# Close the document
doc.close()
