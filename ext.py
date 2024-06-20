import os
from PyPDF2 import PdfFileReader
from langchain.document_loaders import PDFLoader

def extract_text_from_pdf(pdf_path, start_page, end_page):
    loader = PDFLoader.from_file(pdf_path)
    document = loader.load()
    text = ""
    for page_number in range(start_page, end_page + 1):
        page = document.pages[page_number - 1]
        text += page.extract_text() + "\n"
    return text

def save_text_to_file(text, folder, filename):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as file:
        file.write(text)

def process_pdfs(pdf_paths, page_ranges, section_name, folder_name):
    for pdf_path in pdf_paths:
        start_page, end_page = page_ranges
        text = extract_text_from_pdf(pdf_path, start_page, end_page)
        filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_{section_name}.txt"
        save_text_to_file(text, folder_name, filename)

def main():
    # Define your PDF paths
    pdf_paths = [
        "path_to_pdf1.pdf",
        "path_to_pdf2.pdf",
        "path_to_pdf3.pdf",
        "path_to_pdf4.pdf",
        "path_to_pdf5.pdf",
        "path_to_pdf6.pdf",
        "path_to_pdf7.pdf",
        "path_to_pdf8.pdf",
        "path_to_pdf9.pdf"
    ]

    # Define the page ranges for each section
    investor_presentation_pages = (1, 3)  # Example page range for investor presentation
    earning_release_pages = (4, 6)  # Example page range for earning release
    recent_news_pages = (7, 9)  # Example page range for recent news

    # Define folders for each section
    investor_presentation_folder = "Investor_Presentation"
    earning_release_folder = "Earning_Release"
    recent_news_folder = "Recent_News"

    # Process each section and save the text files in the respective folders
    process_pdfs(pdf_paths, investor_presentation_pages, "investor_presentation", investor_presentation_folder)
    process_pdfs(pdf_paths, earning_release_pages, "earning_release", earning_release_folder)
    process_pdfs(pdf_paths, recent_news_pages, "recent_news", recent_news_folder)

if __name__ == "__main__":
    main()
