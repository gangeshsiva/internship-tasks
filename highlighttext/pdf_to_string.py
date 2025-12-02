
from pdf2image import convert_from_path

from PIL import Image

import pytesseract

# Path to the Tesseract executable (where you installed Tesseract)
pytesseract.pytesseract.tesseract_cmd = "C:\\Tesseract-OCR\\tesseract.exe"



# Convert PDF to a list of images (one image per page)
pdf_path="C:\\Users\\gangeshvar.s\\Desktop\\highlighttext\\input\\AI_11_ISC_2 1.pdf"
pages = convert_from_path(pdf_path,poppler_path="C:\\poppler-22.12.0\\Library\\bin")

full_text = ""

for page_number, page in enumerate(pages, start=1):
    text = pytesseract.image_to_string(page)  # OCR each page
    full_text += f"--- Page {page_number} ---\n{text}\n"

print(full_text)