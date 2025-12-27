import pdfplumber
import os

file_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Disney+\25-Q1-Executive-Commentary_Disney.pdf"

print(f"Checking file: {file_path}")
if not os.path.exists(file_path):
    print("❌ File not found!")
    exit()

try:
    with pdfplumber.open(file_path) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        text = ""
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            print(f"Page {i+1} text length: {len(page_text) if page_text else 0}")
            if page_text:
                text += page_text
        
        print(f"Total text length: {len(text)}")
        if len(text) < 50:
             print("❌ Extraction failed or content is too short (Image PDF?)")
except Exception as e:
    print(f"❌ Error: {e}")
