import pandas as pd
import requests
import json
import os
from tqdm import tqdm
import time
import sys

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master.csv")
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")

# SWITCHING TO LIGHTER MODEL TO WORK WITH 10GB RAM
MODEL_NAME = "phi3:mini" 
OLLAMA_API = "http://localhost:11434/api/generate"

# Categories
CATEGORIES = {
    "Technical Blocking": "Measures to detect or block technical detection of location (VPN, proxy, DNS proxy, IP masking).",
    "Account Action": "Punitive measures against accounts (termination, suspension, verification demands).",
    "Price Discrimination": "Differences in pricing based on region, currency, or purchasing power.",
    "Content Licensing": "Geographic restriction of content availability (e.g. 'not available in your region').",
    "Legitimate Portability": "Rules allowing temporary access while traveling (e.g. EU Portability Regulation, 30-day travel).",
    "Regulatory Compliance": "References to local laws, tax/VAT compliance, or export controls.",
    "User Workaround": "Descriptions of users bypassing restrictions (using VPNs, changing store region).",
    "General Terms": "Standard legal text, general marketing, or unrelated content not fitting specific geo-arbitrage categories."
}

SYSTEM_PROMPT = f"""Classify into EXACTLY ONE category. Return ONLY JSON: {{"category": "...", "confidence": 0.0}}

CATEGORIES:
1. Technical Blocking: {CATEGORIES['Technical Blocking']}
2. Account Action: {CATEGORIES['Account Action']}
3. Price Discrimination: {CATEGORIES['Price Discrimination']}
4. Content Licensing: {CATEGORIES['Content Licensing']}
5. Legitimate Portability: {CATEGORIES['Legitimate Portability']}
6. Regulatory Compliance: {CATEGORIES['Regulatory Compliance']}
7. User Workaround: {CATEGORIES['User Workaround']}
8. General Terms: {CATEGORIES['General Terms']}
"""

def classify_sentence(sentence, retries=2):
    if not isinstance(sentence, str) or len(sentence) < 10:
        return "Invalid", 0.0

    prompt = f"{SYSTEM_PROMPT}\n\nSENTENCE: \"{sentence}\"\n\nJSON:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_predict": 50}
    }

    for attempt in range(retries):
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                try:
                    data = json.loads(content)
                    return data.get("category", "Unclassified"), data.get("confidence", 0.0)
                except:
                    return "ParseError", 0.0
            else:
                return f"ServerError_{response.status_code}", 0.0
        except Exception as e:
            time.sleep(1)
            
    return "ConnectionError", 0.0

def main():
    print(f"Loading data...")
    input_df = pd.read_csv(INPUT_FILE)
    
    if os.path.exists(OUTPUT_FILE):
        output_df = pd.read_csv(OUTPUT_FILE)
        # --- CRITICAL: CLEAR PREVIOUS "Error" ENTRIES ---
        # If the user saw "Error" or "ConnectionError", we need to reset them so we can retry
        error_mask = output_df['New_Category'].isin(["Error", "ConnectionError", "ServerError_500", "ParseError"])
        if error_mask.any():
            print(f"Clearing {error_mask.sum()} error entries to retry...")
            output_df.loc[error_mask, 'New_Category'] = ""
    else:
        output_df = input_df.copy()
        output_df['New_Category'] = ""
        output_df['Confidence'] = 0.0

    # Resume Logic
    output_df['New_Category'] = output_df['New_Category'].fillna("")
    todo_indices = output_df[output_df['New_Category'] == ""].index
    print(f"Pending rows: {len(todo_indices)}")

    if len(todo_indices) == 0:
        print("Done.")
        return

    consecutive_errors = 0
    try:
        pbar = tqdm(total=len(todo_indices))
        for idx in todo_indices:
            cat, conf = classify_sentence(output_df.at[idx, 'Sentence'])
            
            # Circuit Breaker
            if "Error" in cat or "ServerError" in cat:
                consecutive_errors += 1
                if consecutive_errors > 5:
                    print("\n[CRITICAL ERROR] Ollama is failing repeatedly (probably Memory/Driver issue). Stopping to prevent polluting CSV.")
                    break
            else:
                consecutive_errors = 0

            output_df.at[idx, 'New_Category'] = cat
            output_df.at[idx, 'Confidence'] = conf
            
            pbar.update(1)
            if idx % 10 == 0:
                output_df.to_csv(OUTPUT_FILE, index=False)
                
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        output_df.to_csv(OUTPUT_FILE, index=False)
        print("Saved.")

if __name__ == "__main__":
    main()
