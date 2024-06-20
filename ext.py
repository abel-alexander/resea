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
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as file:
        file.write(text)

def process_pdfs(pdf_paths_with_ranges, section_name):
    folder = section_name.replace(" ", "_").lower()
    for pdf_path, (start_page, end_page) in pdf_paths_with_ranges.items():
        text = extract_text_from_pdf(pdf_path, start_page, end_page)
        filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_{section_name}.txt"
        save_text_to_file(text, folder, filename)

def main():
    # Define your PDF paths with page ranges for each section
    investor_presentation = {
        "path_to_pdf1.pdf": (1, 3),
        "path_to_pdf2.pdf": (2, 4),
        "path_to_pdf3.pdf": (3, 5),
        "path_to_pdf4.pdf": (1, 2),
        "path_to_pdf5.pdf": (2, 3),
        "path_to_pdf6.pdf": (3, 4),
        "path_to_pdf7.pdf": (1, 3),
        "path_to_pdf8.pdf": (2, 4),
        "path_to_pdf9.pdf": (3, 5)
    }

    earning_release = {
        "path_to_pdf1.pdf": (4, 6),
        "path_to_pdf2.pdf": (5, 7),
        "path_to_pdf3.pdf": (6, 8),
        "path_to_pdf4.pdf": (4, 5),
        "path_to_pdf5.pdf": (5, 6),
        "path_to_pdf6.pdf": (6, 7),
        "path_to_pdf7.pdf": (4, 6),
        "path_to_pdf8.pdf": (5, 7),
        "path_to_pdf9.pdf": (6, 8)
    }

    recent_news = {
        "path_to_pdf1.pdf": (7, 9),
        "path_to_pdf2.pdf": (8, 10),
        "path_to_pdf3.pdf": (9, 11),
        "path_to_pdf4.pdf": (7, 8),
        "path_to_pdf5.pdf": (8, 9),
        "path_to_pdf6.pdf": (9, 10),
        "path_to_pdf7.pdf": (7, 9),
        "path_to_pdf8.pdf": (8, 10),
        "path_to_pdf9.pdf": (9, 11)
    }

    # Process each section and save the text files in respective folders
    process_pdfs(investor_presentation, "Investor Presentation")
    process_pdfs(earning_release, "Earning Release")
    process_pdfs(recent_news, "Recent News")

if __name__ == "__main__":
    main()
