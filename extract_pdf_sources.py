
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

files = [
    "Theoretical Research.pdf",
    "Research Overview.pdf"
]


with open("extracted_sources_utf8.txt", "w", encoding="utf-8") as outfile:
    for f in files:
        outfile.write(f"--- EXTRACTING FROM {f} ---\n")
        content = extract_text_from_pdf(f)
        outfile.write(content + "\n")
        outfile.write("\n" + "="*50 + "\n")
print("Extraction complete.")
