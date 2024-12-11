def convert_pdf_to_images(pdf_path: str) -> List[np.ndarray]:
    """
    Converts each page of a PDF into a grayscale image.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    
    Returns:
    - List of grayscale images (numpy arrays) representing the PDF pages.
    """
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        images.append(gray_image)

    pdf_document.close()
    return images

def detect_table_regions(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detects table-like regions in an image using morphological transformations.
    
    Parameters:
    - image: A binary or grayscale image (numpy array).
    
    Returns:
    - List of bounding boxes (x, y, width, height) for detected table regions.
    """
    # Preprocess the image
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Define kernels for detecting horizontal and vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, image.shape[0] // 30))
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image.shape[1] // 30, 1))

    # Detect vertical and horizontal lines
    vertical_lines = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    horizontal_lines = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Combine detected lines to form a table grid
    table_grid = cv2.add(vertical_lines, horizontal_lines)

    # Find contours of the table regions
    contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by size to eliminate noise
    table_boxes = [
        cv2.boundingRect(contour)
        for contour in contours
        if cv2.contourArea(contour) > image.size * 0.001
    ]

    return table_boxes

def extract_and_save_table_images(pdf_path: str, output_dir: str):
    """
    Extracts table-like regions from a PDF and saves them as individual image files.
    
    Parameters:
    - pdf_path: Path to the input PDF file.
    - output_dir: Directory where the extracted table images will be saved.
    """
    # Convert PDF to images
    page_images = convert_pdf_to_images(pdf_path)

    # Iterate through each page and detect table regions
    for page_number, image in enumerate(page_images):
        table_boxes = detect_table_regions(image)

        for i, (x, y, w, h) in enumerate(table_boxes):
            # Crop the table region
            table_image = image[y:y+h, x:x+w]
            
            # Save the table region as an image file
            output_path = f"{output_dir}/page_{page_number + 1}_table_{i + 1}.png"
            cv2.imwrite(output_path, table_image)
            print(f"Saved table image: {output_path}")
