import pandas as pd
import requests
import json
import os
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIGURATION ---
BASE_PATH = r"Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master.csv")
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")

API_KEY = "AIzaSyDnU_8SoiS_XSR7eIQSmYoEZhCVtKlAM1Y" 
MODEL_NAME = "gemini-3-flash-preview" # Validated from API list
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

BATCH_SIZE = 10      # Maximize batch size
MAX_WORKERS = 10     # Maximize concurrency (1000 RPM limit)

CATEGORIES = {
    "Technical Blocking": "Measures/Technologies used to detect or block the specific use of VPNs/Proxies.",
    "Legal Threat": "Explicit threats of account termination, suspension, or legal action for using circumvention tools.",
    "Price Discrimination": "Differences in pricing based on region, currency, or purchasing power.",
    "Content Licensing": "Geographic restriction of content availability (e.g. 'not available in your region') due to rights.",
    "Legitimate Portability": "Rules allowing temporary access while traveling (e.g. EU Portability Regulation).",
    "Regulatory Compliance": "References to local laws, tax/VAT compliance, or export controls.",
    "User Workaround": "Descriptions of users bypassing restrictions (using VPNs, changing store region).",
    "Security Risk": "(Service Provider Frame) Arguments that VPNs/Proxies are unsafe, malicious, or compromise user data.",
    "Privacy/Security": "(VPN Provider Frame) Arguments focusing on encryption, anonymity, and protection from surveillance.",
    "General Terms": "Standard legal text, general marketing, or unrelated content."
}

SYSTEM_PROMPT = f"""You are a scientific classifier.
CATEGORIES:
1. Technical Blocking: {CATEGORIES['Technical Blocking']}
2. Legal Threat: {CATEGORIES['Legal Threat']}
3. Price Discrimination: {CATEGORIES['Price Discrimination']}
4. Content Licensing: {CATEGORIES['Content Licensing']}
5. Legitimate Portability: {CATEGORIES['Legitimate Portability']}
6. Regulatory Compliance: {CATEGORIES['Regulatory Compliance']}
7. User Workaround: {CATEGORIES['User Workaround']}
8. Security Risk: {CATEGORIES['Security Risk']}
9. Privacy/Security: {CATEGORIES['Privacy/Security']}
10. General Terms: {CATEGORIES['General Terms']}

INSTRUCTIONS:
- Return a JSON array of objects for the sentences in EXACT order.
- Format: [ {{ "category": "Category Name", "confidence": 0.9 }}, ... ]
"""

# Session with retry
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def classify_batch(batch_indices, batch_sentences):
    formatted_input = "\n".join([f"{i+1}. {s}" for i, s in enumerate(batch_sentences)])
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\nSENTENCES:\n{formatted_input}\nJSON OUTPUT:"}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = session.post(API_URL, json=payload, timeout=30) # Standard timeout
        response.raise_for_status()
        results = json.loads(response.json()['candidates'][0]['content']['parts'][0]['text'])
        
        # Validation
        if len(results) != len(batch_sentences):
            return batch_indices, [{"category": "Error", "confidence": 0}] * len(batch_sentences)
            
        return batch_indices, results
        
    except Exception as e:
        print(f"Error: {e}")
        return batch_indices, [{"category": f"Error: {str(e)}", "confidence": 0}] * len(batch_sentences)

def main():
    print("--- STARTING FAST CLASSIFICATION (Threaded) ---")
    
    # Load Data
    if os.path.exists(OUTPUT_FILE):
        df = pd.read_csv(OUTPUT_FILE)
        # Process rows that are empty or Errors
        mask = df['New_Category'].isna() | df['New_Category'].isin(['', 'Unclassified', 'Error', 'API_Error'])
        indices_to_process = df[mask].index.tolist()
    else:
        df = pd.read_csv(INPUT_FILE)
        df['New_Category'] = ""
        df['Confidence'] = 0.0
        indices_to_process = df.index.tolist()
        
    print(f"Remaining rows: {len(indices_to_process)}")
    
    # Batching
    batches = []
    for i in range(0, len(indices_to_process), BATCH_SIZE):
        batch_idxs = indices_to_process[i : i + BATCH_SIZE]
        batch_sentences = [df.at[idx, 'Sentence'] for idx in batch_idxs]
        batches.append((batch_idxs, batch_sentences))
        
    print(f"Processing {len(batches)} batches with {MAX_WORKERS} workers...")
    
    counter = 0
    save_interval = 50
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all inputs
        future_to_batch = {executor.submit(classify_batch, b[0], b[1]): b for b in batches}
        
        for future in concurrent.futures.as_completed(future_to_batch):
            indices, results = future.result()
            
            for i, idx in enumerate(indices):
                if i < len(results):
                    df.at[idx, 'New_Category'] = results[i].get('category', 'Error')
                    df.at[idx, 'Confidence'] = results[i].get('confidence', 0.0)
            
            counter += 1
            if counter % 10 == 0:
                print(f"Progress: {counter}/{len(batches)} batches", end='\r')
                
            if counter % save_interval == 0:
                df.to_csv(OUTPUT_FILE, index=False)
                
    df.to_csv(OUTPUT_FILE, index=False)
    print("\nDone! Saved.")

if __name__ == "__main__":
    main()
