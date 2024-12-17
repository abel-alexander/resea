import fitz  # PyMuPDF for PDFs
import re

def process_toc_page(pdf_path):
    """
    Process the TOC pages (limited to Page 1 and 2), identify hyperlinks, and extract targets.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: Reconstructed TOC with titles and target pages.
    """
    pdf = fitz.open(pdf_path)
    toc_entries = []
    
    for page_num in range(min(2, len(pdf))):  # Check only Page 1 and Page 2
        page = pdf[page_num]
        text = page.get_text("text")
        links = page.get_links()
        
        # Step 1: Check if 'Table of Contents' exists
        if "Table of Contents" in text:
            print(f"TOC Found on Page {page_num + 1}")
            
            # Step 2: Process hyperlinks if more than 3 exist
            if len(links) > 3:
                print(f"Processing {len(links)} hyperlinks on Page {page_num + 1}...")
                lines = text.split("\n")
                
                # Step 3: Extract TOC titles and their targets
                for link in links:
                    target_page = link.get("page", None)
                    if target_page is not None:
                        # Match TOC format: '1. Title' or 'Title'
                        for line in lines:
                            if re.match(r"^\d+\.\s+.+|^[A-Za-z].+", line):
                                toc_entries.append({
                                    "Title": line.strip(),
                                    "Target Page": target_page + 1  # Convert to 1-based index
                                })
                                break

    pdf.close()
    return toc_entries


def format_clean_toc(toc_entries):
    """
    Format TOC entries into a clean, readable format.
    Args:
        toc_entries (list): List of TOC entries with titles and pages.
    """
    print("\nCleaned Table of Contents:")
    for entry in toc_entries:
        print(f"- {entry['Title']} (Page: {entry['Target Page']})")


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path
toc_entries = process_toc_page(pdf_path)
format_clean_toc(toc_entries)
