import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Performance_Apparel_P18.pdf"
doc = fitz.open(pdf_path)

# Analyze the first page (assuming it contains the ToC)
toc_page_number = 0  # Zero-indexed
page = doc[toc_page_number]

# Extract links
links = page.get_links()

# Iterate over links and resolve their destinations
for i, link in enumerate(links):
    print(f"Raw link: {link}")  # Debugging information
    if 'page' in link:  # Direct page link
        # Ensure the destination page is an integer
        destination_page = int(link['page']) if link['page'] is not None else None
        if destination_page is not None:
            print(f"Link {i+1} points to page {destination_page + 1} (1-indexed).")
        else:
            print(f"Link {i+1} does not have a valid page destination.")
    elif 'uri' in link:  # External URL
        uri = link['uri']
        print(f"Link {i+1} points to external URL: {uri}")
    else:
        print(f"Link {i+1} has an unknown or unsupported type: {link}")

# Close the document
doc.close()
