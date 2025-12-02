from PIL import Image

import pytesseract

# Path to the Tesseract executable (where you installed Tesseract)
pytesseract.pytesseract.tesseract_cmd = "C:\\Tesseract-OCR\\tesseract.exe"

# Open image
img = Image.open("C:\\Users\\gangeshvar.s\\Pictures\\Screenshots\\Screenshot 2025-12-02 144150.png")

# Extract text
text = pytesseract.image_to_string(img)

print(text)