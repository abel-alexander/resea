import fitz  # PyMuPDF for PDFs
import re

def extract_toc_levels(pdf_path):
    """
    Extract TOC and organize it into Level 1 and Level 2 based on hyperlinks under 'Table of Contents'.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: Structured TOC with Level 1 and Level 2 groupings.
    """
    pdf = fitz.open(pdf_path)
    toc_structure = {}
    
    for page_num in range(min(2, len(pdf))):  # Limit to Page 1 and Page 2
        page = pdf[page_num]
        text = page.get_text("text")
        links = page.get_links()

        # Step 1: Check for 'Table of Contents'
        if "Table of Contents" in text:
            print(f"TOC Found on Page {page_num + 1}")
            lines = text.split("\n")

            level1 = None  # To track current Level 1 title
            link_targets = [link.get("page", None) for link in links]  # Debug: Page targets
            print(f"Link Targets: {link_targets}")  # Debug: Show page targets
            
            link_idx = 0  # Track hyperlinks to Level 2 entries
            for line in lines:
                if re.match(r"^\d+\.\s+.+", line):  # Match '1. Birkenstock'
                    level1 = line.strip()
                    toc_structure[level1] = []
                elif re.match(r"^\s+\d+\.\s+.+", line):  # Match indented '1 Earnings Report'
                    if level1 and link_idx < len(link_targets):
                        toc_structure[level1].append({
                            "Title": line.strip(),
                            "Page": link_targets[link_idx]  # Attach hyperlink target
                        })
                        link_idx += 1

    pdf.close()
    return toc_structure


def print_clean_toc(toc_structure):
    """
    Print the TOC structure without page numbers for clean output.
    Args:
        toc_structure (dict): Structured TOC with Level 1 and Level 2 entries.
    """
    print("\nCleaned Table of Contents:")
    for level1, level2_items in toc_structure.items():
        print(level1)
        for item in level2_items:
            print(f"   - {item['Title']}")


def get_toc(toc_structure):
    """
    Return the structured Table of Contents in a format without page numbers.
    Args:
        toc_structure (dict): Structured TOC with Level 1 and Level 2 entries.
    Returns:
        dict: Cleaned TOC without page numbers.
    """
    clean_toc = {}
    for level1, level2_items in toc_structure.items():
        clean_toc[level1] = [item['Title'] for item in level2_items]
    return clean_toc


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF path
toc_structure = extract_toc_levels(pdf_path)

# Debugging output with page numbers
print_clean_toc(toc_structure)  # Output without page numbers
clean_toc = get_toc(toc_structure)  # Clean TOC for further use

# Example: View clean TOC structure
print("\nget_toc Result:")
print(clean_toc)
