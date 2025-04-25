from pdf2image import convert_from_path
import pytesseract

# Convert all pages of the PDF to images
pages = convert_from_path('./tealbook.pdf')

# Initialize an empty string to store OCR output
extracted_text = ""

# Perform OCR on each page image
for page in pages:
    extracted_text += pytesseract.image_to_string(page)

# Print out all the extracted text
print(extracted_text)


