import io
import fitz  # PyMuPDF
from PIL import Image
import cv2
import numpy as np

# Step 1: Preprocess the Page Image
def preprocess_page_image(page_image):
    """
    Preprocess the full PDF page image for logo detection.
    :param page_image: Input image (PIL Image or numpy array) of the PDF page.
    :return: Preprocessed grayscale image.
    """
    page_array = np.array(page_image)
    if len(page_array.shape) == 3:  # Convert RGB to Grayscale
        page_array = cv2.cvtColor(page_array, cv2.COLOR_RGB2GRAY)
    return page_array

# Step 2: Extract Regions of Interest (ROIs)
def get_regions_of_interest(page_image):
    """
    Detect regions of interest (ROIs) from a full PDF page image.
    :param page_image: Grayscale numpy array.
    :return: List of bounding boxes for ROIs.
    """
    _, thresh = cv2.threshold(page_image, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 50 < w < 1000 and 50 < h < 1000:  # Filter small and overly large regions
            rois.append((x, y, w, h))
    return rois

# Step 3: Detect Logos in ROIs
def detect_logos_in_rois(page_image, rois, logo_templates):
    """
    Detect logos in the regions of interest (ROIs) of a PDF page.
    :param page_image: Grayscale page image (numpy array).
    :param rois: List of bounding boxes for ROIs.
    :param logo_templates: Dictionary of logo templates.
    :return: List of detected logos.
    """
    detected_logos = []
    for x, y, w, h in rois:
        roi = page_image[y:y+h, x:x+w]
        roi_pil = Image.fromarray(roi)
        detected = detect_logos_with_multiple_templates(logo_templates, roi_pil)
        detected_logos.extend(detected)
    return detected_logos

# Step 4: Detect Logos with Multiple Templates
def detect_logos_with_multiple_templates(logo_templates, test_image):
    """
    Detect logos in a test image using multiple logo templates.
    :param logo_templates: List of paths to logo template images.
    :param test_image: Input image (PIL Image or numpy array).
    :return: List of detected logo names.
    """
    detected_logos = []
    test_img = np.array(test_image)
    if len(test_img.shape) == 3:  # Convert RGB to Grayscale
        test_img = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)

    for logo_name, template_path in logo_templates.items():
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise ValueError(f"Template image at {template_path} could not be loaded.")

        kp1, desc1 = extract_sift_features(template)
        kp2, desc2 = extract_sift_features(test_img)
        good_matches = match_features(desc1, desc2)
        if len(good_matches) > 10:  # Match threshold
            detected_logos.append(logo_name)

    return detected_logos

# Step 5: Extract SIFT Features
def extract_sift_features(image):
    """
    Extracts SIFT features from an image.
    :param image: Input image (numpy array).
    :return: Keypoints and descriptors.
    """
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return keypoints, descriptors

# Step 6: Match Features Using FLANN
def match_features(desc1, desc2):
    """
    Matches SIFT descriptors using FLANN-based matcher.
    :param desc1: Descriptors from the first image.
    :param desc2: Descriptors from the second image.
    :return: List of good matches.
    """
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc1, desc2, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
    return good_matches

# Step 7: Process Full Page for Logos
def process_pdf_page_for_logos(page_image, logo_templates):
    """
    Process a full PDF page image to detect logos.
    :param page_image: Input PDF page image (PIL Image).
    :param logo_templates: Dictionary of logo templates.
    :return: List of detected logos.
    """
    preprocessed_page = preprocess_page_image(page_image)
    rois = get_regions_of_interest(preprocessed_page)
    detected_logos = detect_logos_in_rois(preprocessed_page, rois, logo_templates)
    return detected_logos

# Step 8: Extract Images from PDF
def extract_images_from_pdf_range(pdf_path, start_page, end_page):
    """
    Extract images from a range of pages in a PDF.
    :param pdf_path: Path to the PDF file.
    :param start_page: Starting page number (1-based index).
    :param end_page: Ending page number (1-based index, inclusive).
    :return: List of extracted images with their page numbers and indices.
    """
    images = []
    pdf_file = fitz.open(pdf_path)
    for page_index in range(start_page - 1, end_page):
        page = pdf_file[page_index]
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append((image, page_index + 1, img_index))
    pdf_file.close()
    return images

# Step 9: Main Function
def main():
    # Logo templates
    logo_templates = {
        "Nike": "nike_logo.png",
        "Adidas": "adidas_logo.png"
    }

    # PDF file and page range
    pdf_path = "example.pdf"
    start_page = 1
    end_page = 5

    # Extract images from the specified page range
    images = extract_images_from_pdf_range(pdf_path, start_page, end_page)

    # Detect logos on each page
    for image, page, _ in images:
        detected_logos = process_pdf_page_for_logos(image, logo_templates)
        if detected_logos:
            print(f"Page {page} contains the following logos: {', '.join(set(detected_logos))}")
        else:
            print(f"Page {page} contains no detected logos.")

# Run the main function
if __name__ == "__main__":
    main()
