import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Apparel_2PIB.pdf"
doc = fitz.open(pdf_path)

# Extract the Table of Contents (ToC) as a list of [level, title, page]
toc = doc.get_toc()  # Returns a list of [level, title, page]

# Extract links from the ToC page
toc_page_number = 0  # Adjust if ToC spans multiple pages
toc_page = doc[toc_page_number]
links = toc_page.get_links()

# Create a dictionary from the ToC for fast lookup {page_number: title}
toc_dict = {entry[2]: entry[1] for entry in toc}  # {page_number: title}

# List to store matched results
matched_results = []

# Iterate over links from the ToC page
for link in links:
    try:
        if "page" in link and link["page"] is not None:
            # Get the destination page (convert to 1-indexed)
            destination_page = int(link["page"]) + 1
            
            # Check if this page is in the ToC
            if destination_page in toc_dict:
                title = toc_dict[destination_page]  # Get the title
                matched_results.append((destination_page, title))
    except Exception as e:
        print(f"Error processing link: {link}. Error: {e}")

# Print the matched results
print("Matched Results:")
for page, title in matched_results:
    print(f"Page {page}: {title}")

# Optionally, write the results to a file
with open("matched_results.txt", "w") as output_file:
    for page, title in matched_results:
        output_file.write(f"Page {page}: {title}\n")

# Close the document
doc.close()
