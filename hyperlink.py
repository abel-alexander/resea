import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Apparel_2PIB.pdf"
doc = fitz.open(pdf_path)

# Extract the Table of Contents
toc = doc.get_toc()  # Returns a list of [level, title, page]

# Extract links from the ToC page(s)
toc_page_number = 0  # Adjust if ToC spans multiple pages
toc_page = doc[toc_page_number]
links = toc_page.get_links()

# Build a dictionary of ToC entries for easy lookup
toc_dict = {entry[2]: entry[1] for entry in toc}  # {page_number: title}

# Match links with ToC entries
matched_toc_links = []
for link in links:
    if "page" in link:  # Ensure the link points to a page
        destination_page = link["page"] + 1  # Convert to 1-indexed page
        if destination_page in toc_dict:
            title = toc_dict[destination_page]
            matched_toc_links.append(f"{title}, Page {destination_page}")

# Print the matched ToC links
print("Matched ToC Links:")
for entry in matched_toc_links:
    print(entry)

# Optionally write the matched ToC to a file
with open("matched_toc_links.txt", "w") as output_file:
    output_file.write("\n".join(matched_toc_links))

# Close the document
doc.close()
