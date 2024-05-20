import pandas as pd
from fpdf import FPDF

def save_sheet_as_pdf(excel_file, sheet_name, output_pdf):
    # Read the sheet into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Create a PDF object in landscape mode
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Calculate column widths
    col_widths = pdf.w / len(df.columns)
    
    # Add header
    for col_name in df.columns:
        pdf.cell(col_widths, 10, col_name, border=1)
    pdf.ln()
    
    # Add rows
    for row in df.itertuples(index=False, name=None):
        for cell in row:
            pdf.cell(col_widths, 10, str(cell), border=1)
        pdf.ln()
    
    # Save the PDF
    pdf.output(output_pdf)

def convert_excel_to_pdf(excel_file):
    # Load the Excel file
    xls = pd.ExcelFile(excel_file)
    
    # Iterate through each sheet and save as PDF
    for sheet_name in xls.sheet_names:
        output_pdf = f"{sheet_name}.pdf"
        save_sheet_as_pdf(excel_file, sheet_name, output_pdf)
        print(f"Saved {sheet_name} as {output_pdf}")

# Path to your Excel file
excel_file = 'your_excel_file.xlsx'

# Convert Excel sheets to PDF
convert_excel_to_pdf(excel_file)
