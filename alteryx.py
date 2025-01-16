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
last_broker_title = None  # Keep track of the last detected "Broker" or similar title

# Iterate over links and match with ToC
for link in links:
    try:
        if "page" in link and link["page"] is not None:
            destination_page = int(link["page"]) + 1  # Convert to 1-indexed
            # Check if the page exists in the ToC dictionary
            if destination_page in toc_dict:
                title = toc_dict[destination_page]
                matched_results.append((destination_page, title))
                # Update the last broker title
                last_broker_title = title
            else:
                # No ToC match, extract text from the page and assign a fallback title
                page = doc[destination_page - 1]  # Convert back to 0-indexed
                page_text = page.get_text("text")
                # Extract the first 100 characters for a quick summary
                snippet = page_text[:100].strip()

                # Generate a fallback title
                if last_broker_title:
                    dynamic_title = f"{last_broker_title} - Supplemental Content"
                else:
                    dynamic_title = f"Uncategorized - Page {destination_page}"

                matched_results.append((destination_page, dynamic_title))
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
