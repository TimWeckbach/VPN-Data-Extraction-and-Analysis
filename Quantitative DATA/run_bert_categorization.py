import pandas as pd
import torch
from transformers import pipeline
from tqdm import tqdm
import os
import sys

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_BERT.csv")

# Use the EXACT same categories as Gemini for fair comparison
CANDIDATE_LABELS = [
    "Technical Blocking",
    "Account Action",
    "Price Discrimination",
    "Content Licensing",
    "Legitimate Portability",
    "Regulatory Compliance",
    "User Workaround",
    "General Terms"
]

# Model from your archival script
MODEL_NAME = "facebook/bart-large-mnli" 
BATCH_SIZE = 8 # Adjust based on RAM/VRAM

def main():
    print("--- STARTING BERT (Zero-Shot) CATEGORIZATION ---")
    
    import torch_directml
    
    # 1. Setup Device (DirectML for AMD)
    try:
        device = torch_directml.device()
        print(f"Loading Model '{MODEL_NAME}' on AMD GPU (DirectML)...")
    except Exception as e:
        print(f"DirectML failed ({e}), falling back to CPU.")
        device = -1
    
    try:
        # Note: transformers pipeline with 'device' object might need explicit integer for CUDA, 
        # but for DirectML/MPS usually pass the device object directly.
        # However, huggingface pipelines support 'device=device_object' in newer versions.
        classifier = pipeline("zero-shot-classification", model=MODEL_NAME, device=device)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 2. Load Data
    print(f"Reading data from {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    # Check if we are resuming
    if os.path.exists(OUTPUT_FILE):
        print(f"Resuming from {OUTPUT_FILE}...")
        df_out = pd.read_csv(OUTPUT_FILE)
    else:
        df_out = df.copy()
        df_out['BERT_Category'] = ""
        df_out['BERT_Score'] = 0.0

    # Filter rows that need processing
    # We process anything where BERT_Category is empty
    to_process_mask = (df_out['BERT_Category'].isna()) | (df_out['BERT_Category'] == "")
    indices_to_process = df_out[to_process_mask].index.tolist()
    
    print(f"Total rows: {len(df_out)}")
    print(f"Rows to process: {len(indices_to_process)}")
    
    if len(indices_to_process) == 0:
        print("All rows already processed.")
        return

    # 3. Processing Loop (Batched)
    # We iterate through the indices in chunks
    pbar = tqdm(total=len(indices_to_process))
    
    for i in range(0, len(indices_to_process), BATCH_SIZE):
        batch_indices = indices_to_process[i : i + BATCH_SIZE]
        
        # Extract sentences
        batch_sentences = []
        valid_batch_indices = []
        
        for idx in batch_indices:
            s = df_out.at[idx, 'Sentence']
            if isinstance(s, str) and len(s) > 5:
                batch_sentences.append(s)
                valid_batch_indices.append(idx)
            else:
                # Mark invalid/empty sentences as "Skipped" or "General Terms"
                df_out.at[idx, 'BERT_Category'] = "General Terms"
                df_out.at[idx, 'BERT_Score'] = 1.0
                
        if not batch_sentences:
            pbar.update(len(batch_indices))
            continue
            
        # Run Classifier
        try:
            results = classifier(batch_sentences, candidate_labels=CANDIDATE_LABELS)
            
            # Update DataFrame
            # output is a list of dicts: {'sequence':..., 'labels': [...], 'scores': [...]}
            for j, res in enumerate(results):
                idx = valid_batch_indices[j]
                top_label = res['labels'][0]
                top_score = res['scores'][0]
                
                df_out.at[idx, 'BERT_Category'] = top_label
                df_out.at[idx, 'BERT_Score'] = top_score
                
        except Exception as e:
            print(f"Error in batch {i}: {e}")
            # Save progress and exit or continue?
            # Let's simple skip this batch in data but print error
            pass
            
        pbar.update(len(batch_indices))
        
        # Save periodically
        if i % (BATCH_SIZE * 10) == 0:
            df_out.to_csv(OUTPUT_FILE, index=False)
            
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"Done! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
