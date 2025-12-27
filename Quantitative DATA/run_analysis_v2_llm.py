import os
import requests
import json
import pandas as pd
import pdfplumber
import nltk
import re
from tqdm import tqdm
import time
import glob
import traceback

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_V8_LLM.csv")
MODEL_NAME = "llama3.1" # Using the one we are pulling
OLLAMA_API = "http://localhost:11434/api/generate" # or /api/chat

# Categories
CATEGORIES = {
    "Technical Blocking": "Measures to detect or block technical detection of location (VPN, proxy, DNS proxy, IP masking).",
    "Account Action": "Punitive measures against accounts (termination, suspension, verification demands).",
    "Price Discrimination": "Differences in pricing based on region, currency, or purchasing power.",
    "Content Licensing": "Geographic restriction of content availability (e.g. 'not available in your region').",
    "Legitimate Portability": "Rules allowing temporary access while traveling (e.g. EU Portability Regulation, 30-day travel).",
    "Regulatory Compliance": "References to local laws, tax/VAT compliance, or export controls.",
    "User Workaround": "Descriptions of users bypassing restrictions (using VPNs, changing store region).",
    "Irrelevant": "Standard legal text, general marketing, or unrelated content."
}

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""You are a precise data creation assistant for a Master Thesis on 'Digital Geo-Arbitrage'. 
Your goal is to map sentences from logic/terms of service/reports into rigid theoretical categories.

CATEGORIES:
1. Technical Blocking: {CATEGORIES['Technical Blocking']}
2. Account Action: {CATEGORIES['Account Action']}
3. Price Discrimination: {CATEGORIES['Price Discrimination']}
4. Content Licensing: {CATEGORIES['Content Licensing']}
5. Legitimate Portability: {CATEGORIES['Legitimate Portability']}
6. Regulatory Compliance: {CATEGORIES['Regulatory Compliance']}
7. User Workaround: {CATEGORIES['User Workaround']}
8. Irrelevant: {CATEGORIES['Irrelevant']}

INSTRUCTIONS:
- Analyze the provided text chunk.
- For EACH sentence that strongly matches a category (excluding Irrelevant), extract the sentence and assign the category.
- Ignore 'Irrelevant' sentences to save space.
- Output purely in JSON format: list of objects {{ "sentence": "...", "category": "..." }}
- If no relevant sentences are found, return empty list [].
"""

# --- HELPERS ---
def extract_text(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
    except Exception as e:
        print(f"Error extracting {pdf_path}: {e}")
    return text

def clean_text(text):
    # Remove CID errors and excessive whitespace
    text = re.sub(r'\(cid:\d+\)', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def chunk_text(sentences, chunk_size=10):
    for i in range(0, len(sentences), chunk_size):
        yield sentences[i:i + chunk_size]

def analyze_chunk_with_ollama(chunk_sentences, retries=3):
    formatted_input = "\n".join([f"- {s}" for s in chunk_sentences])
    prompt = f"{SYSTEM_PROMPT}\n\nTEXT TO ANALYZE:\n{formatted_input}\n\nJSON OUTPUT:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json", # Forces JSON mode in recent Ollama versions
        "options": {
            "temperature": 0.0, # CRITICAL FOR SCIENCE: Deterministic
            "num_ctx": 4096
        }
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            content = result.get('response', '')
            
            # Parse JSON
            try:
                data = json.loads(content)
                # Handle simplified object vs list
                if isinstance(data, dict):
                    # Sometimes model returns {"result": [...]}
                    for k in data:
                        if isinstance(data[k], list):
                            return data[k]
                    return [] # Fallback
                return data
            except json.JSONDecodeError:
                # Fallback clean up
                # Find [...]
                start = content.find('[')
                end = content.rfind(']')
                if start != -1 and end != -1:
                    return json.loads(content[start:end+1])
                
        except Exception as e:
            time.sleep(1)
    return []

# --- MAIN ---
def main():
    print("--- STARTING LLM ANALYSIS PIPELINE ---")
    
    # 1. Init CSV
    if not os.path.exists(OUTPUT_FILE):
        pd.DataFrame(columns=['Source', 'Category', 'Sentence']).to_csv(OUTPUT_FILE, index=False)
        print("Created new dataset file.")
    else:
        print("Appending to existing dataset.")
        
    # 2. Find Files (PDFs only for now for speed/relevance as per request)
    files = glob.glob(os.path.join(BASE_PATH, "**/*.pdf"), recursive=True)
    print(f"Found {len(files)} PDFs.")
    
    processed_count = 0
    
    for fpath in tqdm(files, unit="file"):
        fname = os.path.basename(fpath)
        
        # Skip previously checked? (Optional, currently simplified to just process)
        
        # Extract
        raw_text = extract_text(fpath)
        if len(raw_text) < 100: continue
        
        cleaned = clean_text(raw_text)
        sentences = nltk.sent_tokenize(cleaned)
        
        # Filter tiny sentences
        valid_sentences = [s for s in sentences if len(s) > 40]
        
        # Batch Process
        chunks = list(chunk_text(valid_sentences, chunk_size=15)) # 15 sentences per prompt
        
        file_results = []
        for chunk in chunks:
            extracted_items = analyze_chunk_with_ollama(chunk)
            if extracted_items:
                for item in extracted_items:
                    if 'sentence' in item and 'category' in item:
                        file_results.append({
                            'Source': fname,
                            'Category': item['category'],
                            'Sentence': item['sentence']
                        })
        
        # Save per file to avoid data loss
        if file_results:
            df = pd.DataFrame(file_results)
            df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            processed_count += len(df)
            
    print(f"\nDONE. Processed {len(files)} files. Extracted {processed_count} data points.")

if __name__ == "__main__":
    nltk.download('punkt', quiet=True)
    main()
