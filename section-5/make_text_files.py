import os
import re
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

# Define folders: adjust these folder names as needed.
pdf_folder = "./tbas"          # Folder containing Tealbook A PDF files (e.g., "Jul_TBA.pdf", "March_TBA.pdf")
text_folder = "./text_files"     # Folder to store the output text files (one per page)
os.makedirs(text_folder, exist_ok=True)

# Iterate over PDF files in the pdf_folder that match the naming pattern.
for pdf_file in os.listdir(pdf_folder):
    if pdf_file.endswith("_TBA.pdf"):
        # Extract the month from the filename.
        # For example, if the PDF is named "Jul_TBA.pdf", the month will be "Jul"
        month = pdf_file.split('_')[0]
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Processing file '{pdf_path}' (Month: {month})")

        # Convert the PDF into a list of page images.
        pages = convert_from_path(pdf_path)
        
        # Process each page image with rotation correction and OCR.
        for i, page in enumerate(tqdm(pages, desc=f"Processing pages for {month}")):
            # Use pytesseract's orientation and script detection to check rotation.
            osd_output = pytesseract.image_to_osd(page)
            # Extract the rotation angle using regex.
            match = re.search(r"Rotate: (\d+)", osd_output)
            if match:
                rotation_angle = int(match.group(1))
                if rotation_angle != 0:
                    print(f"Rotating page {i+1} by {rotation_angle} degrees (clockwise correction needed)")
                    # Rotate by negative angle to correct the orientation.
                    page = page.rotate(-rotation_angle, expand=True)
            else:
                print(f"Could not detect rotation angle for page {i+1}. Proceeding without rotation correction.")
            
            # Perform OCR on the (corrected) page image.
            extracted_text = pytesseract.image_to_string(page)
            
            # Save the OCR'd text to a file named using the month and page number.
            text_filename = f"{month}_page{i+1}.txt"
            text_path = os.path.join(text_folder, text_filename)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            
            print(f"Saved text from page {i+1} to '{text_path}'")
