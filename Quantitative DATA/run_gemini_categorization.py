import pandas as pd
import requests
import json
import os
import time

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master.csv")
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")

API_KEY = "AIzaSyDnU_8SoiS_XSR7eIQSmYoEZhCVtKlAM1Y" 
MODEL_NAME = "gemini-3-flash-preview" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

BATCH_SIZE = 30 

CATEGORIES = {
    "Technical Blocking": "Measures/Technologies used to detect or block the specific use of VPNs/Proxies (e.g., 'We use geo-blocking technology', 'Error 403').",
    "Legal Threat": "Explicit threats of account termination, suspension, or legal action for using circumvention tools.",
    "Price Discrimination": "Differences in pricing based on region, currency, or purchasing power.",
    "Content Licensing": "Geographic restriction of content availability (e.g. 'not available in your region') due to rights.",
    "Legitimate Portability": "Rules allowing temporary access while traveling (e.g. EU Portability Regulation, 30-day travel).",
    "Regulatory Compliance": "References to local laws, tax/VAT compliance, or export controls.",
    "User Workaround": "Descriptions of users bypassing restrictions (using VPNs, changing store region).",
    "Security Risk": "(Service Provider Frame) Arguments that VPNs/Proxies are unsafe, malicious, or compromise user data.",
    "Privacy/Security": "(VPN Provider Frame) Arguments focusing on encryption, anonymity, and protection from surveillance.",
    "General Terms": "Standard legal text, general marketing, or unrelated content not fitting specific geo-arbitrage categories."
}

SYSTEM_PROMPT = f"""You are a scientific classifier for a Thesis on 'Digital Geo-Arbitrage'.
Classify a list of sentences into the provided categories. 

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
- Analyze sentences independently.
- Return a JSON array of objects, one for each sentence in the EXACT order provided.
- Format: [ {{ "category": "Category Name", "confidence": 0.9 }}, ... ]
- DO NOT return anything but the JSON array.
"""

def classify_batch(sentences, batch_id="Unknown"):
    # Formulate input
    formatted_input = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nSENTENCES TO CLASSIFY:\n{formatted_input}\n\nJSON ARRAY OUTPUT:"}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        print(f"  > [Batch {batch_id}] Sending Request...", flush=True)
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            if 'candidates' in res_data:
                text_out = res_data['candidates'][0]['content']['parts'][0]['text']
                results = json.loads(text_out)
                if isinstance(results, list):
                    return results
            print(f"  ! [Batch {batch_id}] API Warning: {response.text[:200]}", flush=True)
            return []
        else:
            print(f"  ! [Batch {batch_id}] API Error {response.status_code}", flush=True)
            return []
    except Exception as e:
        print(f"  ! [Batch {batch_id}] Exception: {e}", flush=True)
        return []

def main():
    print(f"--- STARTING DEBUG PIPELINE (Batch Size: {BATCH_SIZE}) ---", flush=True)
    
    if os.path.exists(OUTPUT_FILE):
        df = pd.read_csv(OUTPUT_FILE)
        # Detailed mask to catch all previous errors
        mask = df['New_Category'].str.contains("Error|Connection|Unclassified|Server|404|400|BatchError", na=False) | df['New_Category'].isna() | (df['New_Category'] == "")
        indices = df[mask].index.tolist()
    else:
        df = pd.read_csv(INPUT_FILE)
        df['New_Category'] = ""
        df['Confidence'] = 0.0
        indices = df.index.tolist()

    print(f"Total rows to process: {len(indices)}", flush=True)
    
    # Process in chunks
    total_processed = 0
    
    for i in range(0, len(indices), BATCH_SIZE):
        chunk_indices = indices[i : i + BATCH_SIZE]
        chunk_sentences = [df.at[idx, 'Sentence'] for idx in chunk_indices]
        
        print(f"Processing Batch {i} to {i+BATCH_SIZE}...", flush=True)
        results = classify_batch(chunk_sentences, batch_id=i)
        
        if len(results) == len(chunk_indices):
            for j, res in enumerate(results):
                idx = chunk_indices[j]
                df.at[idx, 'New_Category'] = res.get('category', 'Unclassified')
                df.at[idx, 'Confidence'] = res.get('confidence', 0.0)
            print(f"  > [Batch {i}] Success.", flush=True)
        else:
            print(f"  > [Batch {i}] Mismatch ({len(results)} vs {len(chunk_indices)}). Retrying individually...", flush=True)
            for idx in chunk_indices:
                sentence = df.at[idx, 'Sentence']
                single_res = classify_batch([sentence], batch_id=f"{i}_single")
                if single_res and len(single_res) > 0:
                    res = single_res[0]
                    df.at[idx, 'New_Category'] = res.get('category', 'Unclassified')
                    df.at[idx, 'Confidence'] = res.get('confidence', 0.0)
                else:
                    df.at[idx, 'New_Category'] = "IndividualError"
        
        total_processed += len(chunk_indices)
        
        # Save per batch to see progress
        if i % 50 == 0 or i == 0:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Saved Checkpoint ({total_processed}/{len(indices)})", flush=True)

        # No sleep needed for 1000 RPM unless we get 429 errors
        
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done. Results saved to {OUTPUT_FILE}", flush=True)

if __name__ == "__main__":
    main()
