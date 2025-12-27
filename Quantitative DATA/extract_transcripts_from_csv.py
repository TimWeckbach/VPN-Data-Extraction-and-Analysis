
import pandas as pd
import os

DATA_FILE = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
OUTPUT_DIR = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Extracted_Transcripts"

def extract_transcripts():
    print(f"Reading {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"Error: {e}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # Group by Company and Year (and maybe Source if multiple docs per year)
    # Let's use Source if available to be specific, otherwise Company_Year.
    # The 'Source' column often has filenames like '20-10K_Adobe.pdf'.
    
    # We want to reconstruct "transcripts" (or document text).
    # If the user specifically meant Audio Transcriptions, we should look for 'Earnings Call' or similar doc types.
    
    # Let's just dump everything grouped by 'Source' filename if unique, or Company/Year/Type.
    # Inspecting Source column from previous `head`: '20-10K_Adobe.pdf', '24-Q3-Earnings-Transcript_Adobe.pdf'.
    # It seems 'Source' is a good filename identifier.
    
    grouped = df.groupby('Source')
    
    print(f"Found {len(grouped)} unique sources.")
    
    for source_name, group in grouped:
        # Clean filename
        safe_name = str(source_name).replace('.pdf', '.txt').replace('.docx', '.txt')
        if not safe_name.endswith('.txt'):
            safe_name += ".txt"
            
        output_path = os.path.join(OUTPUT_DIR, safe_name)
        
        # Sort by index to maintain original order (assuming CSV is ordered)
        # or we just join them.
        text_content = "\n".join(group['Sentence'].astype(str).tolist())
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
            
    print(f"Extracted {len(grouped)} transcript files to {OUTPUT_DIR}")

if __name__ == "__main__":
    extract_transcripts()
