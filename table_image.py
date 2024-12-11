import os
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from PIL import Image

# Function to convert a PDF page to an image
def pdf_page_to_image(pdf_path, page_number):
    images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
    image_path = f"page_{page_number}.jpg"
    images[0].save(image_path, 'JPEG')
    return image_path

# (f) Table Detection using PaddleOCR
def paddleocr_table_detection(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(image_path, det=True, rec=True, cls=False)

    print("PaddleOCR Table Detection Output:")
    for line in result[0]:
        print(line)

    # Visualize the detection results (optional)
    from paddleocr.tools.infer.utility import draw_ocr
    import cv2
    import matplotlib.pyplot as plt

    image = cv2.imread(image_path)
    boxes = [line[0] for line in result[0]]
    txts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]

    # Draw bounding boxes
    image_with_boxes = draw_ocr(image, boxes, txts, scores, font_path='path/to/font.ttf')

    # Convert BGR to RGB for displaying with matplotlib
    image_with_boxes = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)

    plt.imshow(image_with_boxes)
    plt.axis('off')
    plt.show()

# Main Script
def main():
    pdf_path = input("Enter the path to the PDF: ")
    page_number = int(input("Enter the page number to process: "))

    # Convert PDF page to image
    image_path = pdf_page_to_image(pdf_path, page_number)
    print(f"Image saved at {image_path}")

    # Run table detection using PaddleOCR
    paddleocr_table_detection(image_path)

if __name__ == "__main__":
    main()
