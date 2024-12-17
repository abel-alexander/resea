import fitz  # PyMuPDF for PDFs
import re

def process_toc_page(pdf_path):
    """
    Process pages with Table of Contents, identify hyperlinks, and extract targets.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: Reconstructed TOC with titles and target pages.
    """
    pdf = fitz.open(pdf_path)
    toc_entries = []
    
    for page_num, page in enumerate(pdf, start=1):
        text = page.get_text("text")
        links = page.get_links()  # Extract hyperlinks
        
        # Step 1: Check if 'Table of Contents' exists on the page
        if "Table of Contents" in text:
            print(f"TOC Found on Page {page_num}")
            
            # Step 2: If more than 3 hyperlinks, process the page
            if len(links) > 3:
                print(f"Processing {len(links)} hyperlinks...")
                
                # Step 3: Extract the TOC titles and targets
                lines = text.split("\n")
                for link in links:
                    target_page = link.get("page", None)  # Get the target page
                    if target_page is not None:
                        # Match TOC format like '1. Title' or 'Title'
                        for line in lines:
                            if re.match(r"^\d+\.\s+.+|^[A-Za-z].+", line):
                                toc_entries.append({"Title": line.strip(), "Target Page": target_page + 1})
                                break

    pdf.close()
    return toc_entries


def format_clean_toc(toc_entries):
    """
    Clean and format TOC entries into a readable format.
    Args:
        toc_entries (list): List of TOC entries.
    """
    print("\nCleaned Table of Contents:")
    for entry in toc_entries:
        print(f"- {entry['Title']} (Page: {entry['Target Page']})")


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path
toc_entries = process_toc_page(pdf_path)
format_clean_toc(toc_entries)
