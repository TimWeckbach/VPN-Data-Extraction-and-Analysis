import pdfplumber
import os
from pypdf import PdfReader

file_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Disney+\25-Q1-Executive-Commentary_Disney.pdf"

print("--- Testing PyPDF ---")
try:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    print(f"PyPDF Total text length: {len(text)}")
    if len(text) > 50:
        print("✅ PyPDF Success!")
        print(f"Sample: {text[:200]}")
    else:
        print("❌ PyPDF Failed (Text too short)")
except Exception as e:
    print(f"❌ PyPDF Error: {e}")
