from pdf2image import convert_from_path
import re
import pytesseract
from tqdm import tqdm

pages = convert_from_path('./tealbook.pdf')

extracted_text = ""

for i, page in tqdm(enumerate(pages)):
    osd_output = pytesseract.image_to_osd(page)
    
    # Extract the rotation angle using regex
    match = re.search(r"Rotate: (\d+)", osd_output)
    if match:
        rotation_angle = int(match.group(1))
        if rotation_angle != 0:
            print(f"Rotating {rotation_angle} degrees (clockwise correction needed)")
            pages[i] = page.rotate(-rotation_angle, expand=True)
    else:
        print("Could not detect rotation angle.")

# Perform OCR on each (corrected) page image
for page in pages:
    extracted_text += pytesseract.image_to_string(page)

print(extracted_text)