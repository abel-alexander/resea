import cv2
import pytesseract
import logging
import re
from typing import List, Tuple, Any

class TableTextExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        pytesseract.pytesseract.tesseract_cmd = r"<path_to_tesseract>"  # Update the path to Tesseract executable

    def _detect_tables(self, image: Any) -> List[Tuple[int, int, int, int]]:
        """
        Detects tables in an image using morphological transformations for line detection
        and contour detection to identify table boundaries.
        """
        try:
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, image.shape[0] // 30))
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image.shape[1] // 30, 1))

            vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
            horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

            table_grid = cv2.add(horizontal_lines, vertical_lines)
            contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            tables = [
                cv2.boundingRect(contour)
                for contour in contours
                if cv2.contourArea(contour) > image.size * 0.001
            ]

            logging.info(f"Detected {len(tables)} tables in the image.")
            return tables

        except Exception as e:
            logging.error("Error during table detection", exc_info=True)
            raise

    def _extract_text_from_tables(self, image: Any, tables: List[Tuple[int, int, int, int]]) -> List[str]:
        """
        Extracts text from specified table regions in an image using OCR.
        """
        try:
            texts = [
                pytesseract.image_to_string(image[y:y + h, x:x + w], lang='eng')
                for x, y, w, h in tables
            ]
            logging.info(f"Extracted text from {len(tables)} tables.")
            return texts

        except Exception as e:
            logging.error("Error extracting text from tables", exc_info=True)
            raise

    def _image_list(self, pdf_path: str) -> List[Any]:
        """
        Converts a PDF to a list of images.
        """
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            return [cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY) for image in images]
        except Exception as e:
            logging.error("Error converting PDF to images", exc_info=True)
            raise

    def extract_tables_and_text(self) -> List[str]:
        """
        Extracts tables and their respective text from the document specified by `self.pdf_path`.
        """
        try:
            logging.info("Starting table and text extraction process.")
            images = self._image_list(self.pdf_path)

            all_tables_text = []
            for image in images:
                tables = self._detect_tables(image)
                texts = self._extract_text_from_tables(image, tables)
                all_tables_text.extend(texts)

            logging.info("Completed table and text extraction process.")
            return all_tables_text

        except Exception as e:
            logging.error("Error in extracting tables and text", exc_info=True)
            raise

    def extracted_data(self) -> List[str]:
        """
        Cleans and returns the extracted text data from tables in the document.
        """
        try:
            logging.info("Starting extracted data processing.")
            raw_texts = self.extract_tables_and_text()

            cleaned_texts = [
                re.sub(r'\s+', ' ', text.strip()) for text in raw_texts
            ]
            logging.info("Completed data extraction and cleaning.")
            return cleaned_texts

        except Exception as e:
            logging.error("Error in extracting data", exc_info=True)
            raise

# Usage example:
# extractor = TableTextExtractor(pdf_path="path_to_pdf")
# data = extractor.extracted_data()
# print(data)
