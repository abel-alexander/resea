from ultralyticsplus import YOLO
import cv2
import pytesseract

# Load the YOLO model
model = YOLO('keremberke/yolov8s-table-extraction')

# Set model parameters
model.overrides['conf'] = 0.25  # NMS confidence threshold
model.overrides['iou'] = 0.45  # NMS IoU threshold
model.overrides['agnostic_nms'] = False  # NMS class-agnostic
model.overrides['max_det'] = 1000  # Maximum number of detections per image

# Path to the image
image_path = 'page_0_image.png'
image = cv2.imread(image_path)

# Perform inference
results = model.predict(image_path)

# Loop through detected tables and extract fixed-width flat text
for idx, box in enumerate(results[0].boxes.xyxy):
    x1, y1, x2, y2 = map(int, box)  # Bounding box coordinates
    cropped_table = image[y1:y2, x1:x2]  # Crop the table region

    # Convert to grayscale for better OCR
    gray_table = cv2.cvtColor(cropped_table, cv2.COLOR_BGR2GRAY)

    # Use Tesseract OCR to extract text with table alignment
    custom_config = r'--psm 6'  # Assumes a single block of text
    extracted_text = pytesseract.image_to_string(gray_table, config=custom_config)

    # Optionally, format the extracted text into a fixed-width layout
    fixed_text = "\n".join(
        ["{: <20} {: <10} {: <10}".format(*line.split()) for line in extracted_text.split("\n") if line.strip()]
    )

    # Print the formatted fixed-width text
    print(f"Fixed-width text from table {idx + 1}:\n{fixed_text}")
