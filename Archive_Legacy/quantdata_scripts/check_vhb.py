import sys
import os

KEYWORDS = [
    "Artificial Intelligence and Law", "ICAIL",
    "Information and Computer Technologies", "ICICM",
    "Web Conference", "WWW",
    "World Wide Web",
    "Electronic Commerce", # common for TIE
    "Information Systems",
    "Management"
]

PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Documents\VHB_Rating_2024_Area_rating_TIE.pdf"

def check_pdf():
    print(f"Checking {PATH}...")
    text = ""
    
    # Try pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(PATH)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print("Extracted text using pypdf.")
    except ImportError:
        # Try PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(PATH)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            print("Extracted text using PyPDF2.")
        except ImportError:
            print("Neither pypdf nor PyPDF2 installed. Cannot read PDF locally.")
            return

    # Search
    found_any = False
    lower_text = text.lower()
    for k in KEYWORDS:
        if k.lower() in lower_text:
            print(f"[MATCH] Found keyword: '{k}'")
            found_any = True
            
    if not found_any:
        print("No keywords matched in the PDF.")
    else:
        print("Done searching.")

if __name__ == "__main__":
    if os.path.exists(PATH):
        check_pdf()
    else:
        print(f"File not found: {PATH}")
