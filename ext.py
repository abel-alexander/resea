import PyPDF2

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfFileReader(file)
        
        # Check if the PDF file is encrypted
        if pdf_reader.isEncrypted:
            pdf_reader.decrypt('')
        
        # Get the total number of pages
        num_pages = pdf_reader.numPages
        
        # Initialize a variable to store the extracted text
        text = ''
        
        # Loop through all the pages and extract text
        for page_num in range(num_pages):
            # Get the page object
            page = pdf_reader.getPage(page_num)
            # Extract text from the page
            text += page.extract_text()
        
        return text

# Example usage
pdf_path = 'path_to_your_pdf_file.pdf'
extracted_text = extract_text_from_pdf(pdf_path)
print(extracted_text)
