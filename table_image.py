import os
import cv2
import fitz  # PyMuPDF
import numpy as np


def convert_pdf_to_images(pdf_path, dpi=200):
    """
    Converts a PDF into grayscale images for each page.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    - dpi: Resolution of the output images.
    
    Returns:
    - List of images (numpy arrays) representing each page of the PDF.
    """
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        images.append(gray_image)

    pdf_document.close()
    return images


def pre_process_image(img, morph_size=(10, 10)):
    """
    Preprocesses the image for table detection.
    Includes dilation to connect text regions and removal of smudges or noise.

    Parameters:
    - img: Input image (as a numpy array).
    - morph_size: Kernel size for dilation.

    Returns:
    - pre: Preprocessed binary image ready for contour detection.
    """
    _, binary = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel_smudge = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_smudge, iterations=1)

    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, morph_size)
    dilated = cv2.dilate(clean, kernel_dilate, iterations=2)

    return dilated


def find_text_boxes(pre, min_text_height_limit=6, max_text_height_limit=40):
    contours, _ = cv2.findContours(pre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []

    for contour in contours:
        box = cv2.boundingRect(contour)
        _, _, _, h = box

        if min_text_height_limit < h < max_text_height_limit:
            boxes.append(box)

    return boxes


def find_table_in_boxes(boxes, cell_threshold=10, min_columns=2):
    rows = {}
    cols = {}

    for box in boxes:
        x, y, w, h = box
        col_key = x // cell_threshold
        row_key = y // cell_threshold

        if col_key not in cols:
            cols[col_key] = []
        cols[col_key].append(box)

        if row_key not in rows:
            rows[row_key] = []
        rows[row_key].append(box)

    table_cells = list(filter(lambda r: len(r) >= min_columns, rows.values()))
    table_cells = [sorted(row, key=lambda b: b[0]) for row in table_cells]
    table_cells = sorted(table_cells, key=lambda r: r[0][1])

    return table_cells


def extract_and_save_table_images(pdf_path, output_dir):
    """
    Detects tables in a PDF and saves them as individual image files.

    Parameters:
    - pdf_path: Path to the PDF file.
    - output_dir: Directory to save the output table images.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images = convert_pdf_to_images(pdf_path)

    for page_number, image in enumerate(images):
        pre_processed = pre_process_image(image)
        text_boxes = find_text_boxes(pre_processed)
        table_cells = find_table_in_boxes(text_boxes)

        for table_index, row in enumerate(table_cells):
            x1 = min(box[0] for box in row)
            y1 = min(box[1] for box in row)
            x2 = max(box[0] + box[2] for box in row)
            y2 = max(box[1] + box[3] for box in row)

            table_image = image[y1:y2, x1:x2]
            output_path = os.path.join(output_dir, f"page_{page_number + 1}_table_{table_index + 1}.png")
            cv2.imwrite(output_path, table_image)
            print(f"Saved table image: {output_path}")


if __name__ == "__main__":
    pdf_path = "path_to_your_pdf.pdf"  # Update with the path to your PDF
    output_dir = "output_tables"      # Update with the desired output directory

    extract_and_save_table_images(pdf_path, output_dir)
