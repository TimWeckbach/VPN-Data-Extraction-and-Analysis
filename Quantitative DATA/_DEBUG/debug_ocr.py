import pdfplumber
import easyocr
import numpy as np
from PIL import Image
import io

file_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Disney+\25-Q1-Executive-Commentary_Disney.pdf"

print("--- Testing OCR extraction ---")
reader = easyocr.Reader(['en'], gpu=True) # use GPU if available

try:
    with pdfplumber.open(file_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        full_text = ""
        
        for i, page in enumerate(pdf.pages):
            # Try getting the image of the page
            # Note: resolution needs to be decent for OCR
            try:
                # 'original' might fail if poppler not installed, let's see
                im = page.to_image(resolution=300).original
                
                print(f"Page {i+1}: Image rendered. Analyzing with EasyOCR...")
                # Convert PIL to bytes or numpy
                img_np = np.array(im)
                
                # Run OCR
                results = reader.readtext(img_np, detail=0) # distinct text lines
                page_text = " ".join(results)
                print(f"  > Found {len(page_text)} chars")
                full_text += page_text + " "
                
            except Exception as e_img:
                print(f"Page {i+1} Render Error: {e_img}")
                # Fallbact: try to find embedded images
                print("  > Trying embedded images...")
                for img_obj in page.images:
                    # pdfplumber provides bounding boxes, not the image data directly easily?
                    # actually it might be hard with pdfplumber alone without poppler to get the pixels.
                    pass

        if len(full_text) > 50:
             print("✅ OCR Success!")
             print(f"Sample: {full_text[:200]}")
        else:
             print("❌ OCR Failed.")

except Exception as e:
    print(f"❌ Error: {e}")
