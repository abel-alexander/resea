import re

def clean_text(text):
    # Remove newline characters
    text = text.replace('\n', ' ')
    
    # Remove unwanted substrings
    text = re.sub(r'/A\.', '', text)
    
    # Remove commas and apostrophes
    text = text.replace(',', '').replace("'", "")
    
    # Optionally, you can remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Example usage
raw_text = """
106Reconciliation of Cash Flow from Operating /A.sso04djusted Free Cash Flow and /A.sso04djusted Free Cash Flow MarginCash flow margin is calculated as adjusted free cash flow divided by revenueCash Flow from Operating /A.sso04ctivitiesCash flow from operating /A.sso04djusted Free Cash Flow/A.sso04djusted Free Cash Flow MarginCash Used to Purchase Property, Plant and Equipment/A.sso04dNDS/zero.tf24aPalantir Technologies Inc./Y.sso04 2023ns 752q4 2023)ns 78,763/n1,918(n4,918)1)ns 75,76304 2023ns 75,76304 Reconciliation of Gross Profit to /A.sso04djusted Gross MarginExcluding Stock-Based Compensation/A.sso04djusted gross margin is calculated as adjusted gross profit divided by revenueGross ProfitNStock-Based Compensation/A.sso04djusted Gross Margin04 2023)ns 497,7111,0018)ns 97,395n9251,829,9028 THOUS./A.sso04dNS) 2023ns 458,0510 2023)ns 426,418n1uni008 8,004 2023ns 9,177n185426,71804 2022)ns 404,313n10,6103 388,780n/A.sso04ppendixne 2/zero.tf24a 8 2023)ns 370,269n10,525n80s 388,780n/A.sso04mplete Information Book1 50 of 106Reconciliation of Gross Profit to /A.sso04djusted Operating MarginExcluding Stock-Based Compensation and Related Employer Payroll Taxesn/A.sso04dUn/A.sso04djusted Operating MarginEmployer Payroll Taxes Related to Stock-Based Compensation/A.sso04djusted Operating Margin04 2023)ns 494,201)564,798)n220,75317,15067/Y.sso04 2023)ns 119,960%163,2728,90904 2023ns 65,79410,n0,074n119,201%135,03510,76004
"""

cleaned_text = clean_text(raw_text)
print(cleaned_text)


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
