
import os

def fix_bib_encoding():
    bib_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\Bibliography.bib"
    
    # Cleaning strategy: remove null bytes directly if reading binary.
    # This converts UTF-16LE (byte-null-byte-null) to ASCII/UTF-8 by dropping the nulls.
    try:
        with open(bib_path, 'rb') as f:
            raw_content = f.read()
            
        if b'\x00' in raw_content:
            print("Detected null bytes, cleaning...")
            clean_content = raw_content.replace(b'\x00', b'').decode('utf-8', errors='ignore')
            
            with open(bib_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            print("File preserved and cleaned.")
        else:
            print("No null bytes found, file likely fine or just UTF-8.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_bib_encoding()
