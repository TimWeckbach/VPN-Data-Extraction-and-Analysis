import pdfplumber
import os

file_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Adobe\22-10K_Adobe.pdf"

print(f"Checking file: {file_path}")
if not os.path.exists(file_path):
    print("❌ File not found!")
    exit()

try:
    with pdfplumber.open(file_path) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        text_sample = ""
        total_len = 0
        for i, page in enumerate(pdf.pages[:5]): # Check first 5 pages
            pt = page.extract_text()
            if pt:
                total_len += len(pt)
                text_sample += pt[:100] + "\n"
        
        print(f"Total extracted length (first 5 pages): {total_len}")
        print(f"Sample:\n{text_sample}")
        
except Exception as e:
    print(f"❌ Error: {e}")
