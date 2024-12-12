import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Public_Information_Book.pdf"
doc = fitz.open(pdf_path)

# Analyze the first page (assuming it contains the ToC)
toc_page_number = 0  # Adjust if ToC spans multiple pages
toc_page = doc[toc_page_number]

# Extract lines of text
lines = toc_page.get_text("text").split("\n")  # Get text line by line

# Extract hyperlinks
links = toc_page.get_links()  # Get all links on the ToC page

# Parse the hierarchical structure
toc_hierarchy = []  # List to store the parsed ToC structure
current_company = None  # To track the current company

for line in lines:
    line = line.strip()
    if line.isdigit():  # Ignore pure numeric lines (e.g., list numbers)
        continue
    if line.endswith(":"):  # Check for company names
        current_company = line[:-1]  # Remove the trailing colon
    elif current_company:  # Add subcategories under the current company
        toc_hierarchy.append((current_company, line))

# Match hyperlinks to ToC structure
new_toc = []
for link, (company, subcategory) in zip(links, toc_hierarchy):
    if "page" in link and link["page"] is not None:
        destination_page = link["page"] + 1  # Convert to 1-indexed
        new_toc.append((company, subcategory, destination_page))

# Print the new ToC
print("Generated Table of Contents:")
for company, subcategory, page in new_toc:
    print(f"{company} - {subcategory}, Page {page}")

# Optionally save the new ToC to a file
with open("generated_toc.txt", "w") as output_file:
    for company, subcategory, page in new_toc:
        output_file.write(f"{company} - {subcategory}, Page {page}\n")

# Close the document
doc.close()
