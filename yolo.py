import os
import cv2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import json
import logging
from typing import List, Tuple, Any, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TableExtractor:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def _image_list_(self) -> List[str]:
        """
        Converts all pages in a PDF file to images.
        """
        try:
            images = convert_from_path(self.pdf_path)
            img_list = []
            for i, image in enumerate(images):
                image_name = f'page_{i + 1}.jpg'
                image.save(image_name, 'JPEG')
                img_list.append(image_name)
            return img_list
        except Exception as e:
            logging.error(f"Error converting PDF to images: {e}")
            raise

    def _preprocess_image_(self, image_path: str) -> Any:
        """
        Preprocesses an image for table detection.
        """
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
        except Exception as e:
            logging.error("Error during preprocessing", exc_info=True)
            raise

    def _detect_tables_(self, image: Any) -> List[Tuple[int, int, int, int]]:
        """
        Detects tables in an image using contours.
        """
        try:
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image.shape[0] / 30)))
            horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image.shape[1] / 30), 1))
            vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
            horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horiz_kernel, iterations=2)
            table_grid = cv2.add(horizontal_lines, vertical_lines)
            contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            tables = [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 1000]
            logging.info(f"Detected {len(tables)} tables in the image.")
            return tables
        except Exception as e:
            logging.error("Error during table detection", exc_info=True)
            raise

    def _extract_text_from_tables_(self, image: Any, tables: List[Tuple[int, int, int, int]]) -> List[str]:
        """
        Extracts text from table regions in an image.
        """
        try:
            texts = []
            for (x, y, w, h) in tables:
                table_image = image[y:y + h, x:x + w]
                text = pytesseract.image_to_string(table_image, lang='eng')
                texts.append(text)
            logging.info(f"Extracted text from {len(tables)} tables.")
            return texts
        except Exception as e:
            logging.error("Error extracting text from tables", exc_info=True)
            raise

    def extract_tables_and_text(self) -> List[str]:
        """
        Extracts tables and their text from the PDF.
        """
        try:
            logging.info("Starting table extraction.")
            images = self._image_list_()
            all_tables_text = []

            for image_path in images:
                preprocessed_image = self._preprocess_image_(image_path)
                tables = self._detect_tables_(preprocessed_image)
                img = cv2.imread(image_path)
                texts = self._extract_text_from_tables_(img, tables)
                all_tables_text.extend(texts)

            logging.info("Completed table extraction.")
            return all_tables_text
        except Exception as e:
            logging.error("Error extracting tables and text", exc_info=True)
            raise

    def save_tables_as_json(self) -> str:
        """
        Saves extracted tables to a JSON file.
        """
        try:
            tables_text = self.extract_tables_and_text()
            cleaned_text = [re.sub(r'\s+', ' ', text).strip() for text in tables_text]
            output_data = {f"table_{i + 1}": text for i, text in enumerate(cleaned_text)}
            output_file = "extracted_tables.json"

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            logging.info(f"Tables saved to {output_file}.")
            return output_file
        except Exception as e:
            logging.error("Error saving tables to JSON", exc_info=True)
            raise

if __name__ == "__main__":
    pdf_path = input("Enter the PDF file path: ")
    extractor = TableExtractor(pdf_path)
    result_file = extractor.save_tables_as_json()
    print(f"Extracted tables saved in {result_file}")
