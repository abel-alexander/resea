import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Apparel_2PIB.pdf"
doc = fitz.open(pdf_path)

# Extract the Table of Contents (ToC) as a list of [level, title, page]
toc = doc.get_toc()  # Returns a list of [level, title, page]

# Build a dictionary for the first matching page number regardless of level
toc_dict = {}
for entry in toc:
    page_number = entry[2]
    if page_number > 0 and page_number not in toc_dict:  # Only keep the first entry for each page
        toc_dict[page_number] = entry[1]  # {page_number: title}

# Extract links from the ToC page
toc_page_number = 0  # Adjust if ToC spans multiple pages
toc_page = doc[toc_page_number]
links = toc_page.get_links()

# List to store matched results
matched_results = []
section_counter = ord('A')  # Start naming unmatched sections as Section A, B, C, ...

# Iterate over links and match with ToC
for link in links:
    try:
        if "page" in link and link["page"] is not None:
            destination_page = int(link["page"]) + 1  # Convert to 1-indexed
            # Check if the page exists in the ToC dictionary
            if destination_page in toc_dict:
                title = toc_dict[destination_page]
                matched_results.append((1, title, destination_page))  # Level 1 in ToC
            else:
                # No ToC match, extract text from the page and generate a fallback title
                page = doc[destination_page - 1]  # Convert back to 0-indexed
                page_text = page.get_text("text").strip()
                if page_text:
                    fallback_title = page_text[:20].replace("\n", " ")  # First 20 characters
                else:
                    fallback_title = f"Section {chr(section_counter)}"  # Section A, B, C...
                    section_counter += 1
                matched_results.append((1, fallback_title, destination_page))
    except Exception as e:
        print(f"Error processing link: {link}. Error: {e}")

# Print the matched results
print("Matched Results:")
for level, title, page in matched_results:
    print(f"Level {level}: {title}, Page {page}")

# Update the ToC in the PDF
doc.set_toc(matched_results)

# Save the updated PDF
output_path = "Updated_" + pdf_path
doc.save(output_path)
print(f"\nUpdated ToC saved to {output_path}")

# Close the document
doc.close()
