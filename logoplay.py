import io
import fitz  # PyMuPDF
from PIL import Image
import cv2
import numpy as np
import os


# Step 1: Extract SIFT features
def extract_sift_features(image):
    """
    Extracts SIFT features from an image.
    :param image: Input image (numpy array).
    :return: Keypoints and descriptors.
    """
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return keypoints, descriptors


# Step 2: Match features using FLANN
def match_features(desc1, desc2):
    """
    Matches SIFT descriptors using FLANN-based matcher.
    :param desc1: Descriptors from the first image.
    :param desc2: Descriptors from the second image.
    :return: List of good matches.
    """
    index_params = dict(algorithm=1, trees=5)  # KDTree for SIFT
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc1, desc2, k=2)

    # Apply Lowe's ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    return good_matches


# Step 3: Detect logos in a test image with multiple templates
def detect_logos_with_multiple_templates(logo_templates, test_image):
    """
    Detect logos in a test image using multiple logo templates.
    :param logo_templates: List of paths to logo template images.
    :param test_image: Input image (PIL Image or numpy array).
    :return: List of detected logo names.
    """
    detected_logos = []

    for logo_name, template_path in logo_templates.items():
        # Read and preprocess template
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        test_img = cv2.cvtColor(np.array(test_image), cv2.COLOR_RGB2GRAY)

        # Extract SIFT features
        kp1, desc1 = extract_sift_features(template)
        kp2, desc2 = extract_sift_features(test_img)

        # Match features
        good_matches = match_features(desc1, desc2)

        # Check for sufficient matches
        match_threshold = 10  # Adjust threshold based on your requirements
        if len(good_matches) > match_threshold:
            detected_logos.append(logo_name)

    return detected_logos


# Step 4: Extract images from PDF within a specified range
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

    # Adjust for 1-based index and ensure valid range
    if start_page < 1 or end_page > len(pdf_file) or start_page > end_page:
        raise ValueError("Invalid page range specified.")

    for page_index in range(start_page - 1, end_page):  # Convert to 0-based index
        page = pdf_file[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append((image, page_index + 1, img_index))  # Save image, page, and index

    pdf_file.close()
    return images


# Step 5: Detect logos in a PDF across multiple templates
def detect_logos_in_pdf_multiple(pdf_path, logo_templates, start_page, end_page):
    """
    Detect multiple logos in a PDF within a specified page range.
    :param pdf_path: Path to the PDF file.
    :param logo_templates: Dictionary of logo names and their template paths.
    :param start_page: Starting page number (1-based index).
    :param end_page: Ending page number (1-based index, inclusive).
    :return: Dictionary mapping page numbers to detected logos.
    """
    images = extract_images_from_pdf_range(pdf_path, start_page, end_page)
    page_logo_matches = {}

    for image, page, index in images:
        detected_logos = detect_logos_with_multiple_templates(logo_templates, image)
        if detected_logos:
            if page not in page_logo_matches:
                page_logo_matches[page] = []
            page_logo_matches[page].extend(detected_logos)

    return page_logo_matches


# Step 6: Log detected logos
def log_detected_logos(page_logo_matches):
    """
    Log the detected logos for each page.
    :param page_logo_matches: Dictionary mapping page numbers to detected logos.
    """
    for page, logos in page_logo_matches.items():
        unique_logos = set(logos)  # Avoid duplicate logos per page
        print(f"Page {page} contains the following logos: {', '.join(unique_logos)}")


# Step 7: Main function to integrate the workflow
def main():
    # Paths to the logo templates
    logo_templates = {
        "Nike": "nike_logo.png",
        "Adidas": "adidas_logo.png",
        "Puma": "puma_logo.png"
    }

    # PDF file and page range
    pdf_path = "example.pdf"
    start_page = 1
    end_page = 10

    # Detect multiple logos
    page_logo_matches = detect_logos_in_pdf_multiple(pdf_path, logo_templates, start_page, end_page)

    # Log results
    if page_logo_matches:
        log_detected_logos(page_logo_matches)
    else:
        print(f"No logos detected in pages {start_page} to {end_page}.")


# Run the main function
if __name__ == "__main__":
    main()




def detect_logos_with_multiple_templates(logo_templates, test_image):
    """
    Detect logos in a test image using multiple logo templates.
    :param logo_templates: List of paths to logo template images.
    :param test_image: Input image (PIL Image or numpy array).
    :return: List of detected logo names.
    """
    detected_logos = []

    # Convert the test image to a numpy array
    test_img = np.array(test_image)
    if len(test_img.shape) == 3:  # RGB image
        test_img = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)
    elif len(test_img.shape) != 2:  # Not grayscale or RGB
        raise ValueError("Invalid test image format. Expected grayscale or RGB.")

    for logo_name, template_path in logo_templates.items():
        # Load and preprocess template
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise ValueError(f"Template image at {template_path} could not be loaded. Check the file path.")

        # Extract SIFT features
        kp1, desc1 = extract_sift_features(template)
        kp2, desc2 = extract_sift_features(test_img)

        # Match features
        good_matches = match_features(desc1, desc2)

        # Check for sufficient matches
        match_threshold = 10  # Adjust threshold based on your requirements
        if len(good_matches) > match_threshold:
            detected_logos.append(logo_name)

    return detected_logos
