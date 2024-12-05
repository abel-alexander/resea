import cv2
import pytesseract
from pytesseract import Output
import os
from tqdm import tqdm

def extract_text_from_top(image, top_percentage=30):
    """Extract text from the top portion of an image."""
    height, width = image.shape[:2]
    top_crop = image[:int(height * (top_percentage / 100.0)), :]  # Crop the top region
    text = pytesseract.image_to_string(top_crop, lang='eng')  # OCR
    return text

def find_company_starting_pages(image_paths, companies):
    """Find the page number where each company's section starts."""
    results = {}
    
    for page_num, image_path in enumerate(tqdm(image_paths, desc="Processing images")):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Warning: Could not read image: {image_path}")
            continue
        
        # Extract text from the top region of the page
        detected_text = extract_text_from_top(image).lower()  # Convert to lowercase for case-insensitive matching
        
        # Check for exact substring match of company names
        for company in companies:
            if company.lower() in detected_text:  # Case-insensitive check
                if company not in results:  # Record the first occurrence
                    results[company] = page_num + 1  # Page numbers are 1-based
                break  # Stop checking once a match is found for this page
    
    return results

# Example usage
image_folder = "output_images"  # Folder containing converted images
image_paths = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder)])
companies = ["J.P. Morgan", "Goldman Sachs", "Barclays"]  # Update this list with your companies

# Find starting pages for each company
starting_pages = find_company_starting_pages(image_paths, companies)

# Output the results
print("\nCompanies and Starting Pages:")
for company, page in starting_pages.items():
    print(f"{company}: Page {page}")
