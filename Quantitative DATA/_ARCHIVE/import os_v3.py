import os
import pdfplumber
import pandas as pd
import nltk
import re
import torch
import torch_directml
import gc
import traceback
import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

# --- SUPPRESS WARNINGS ---
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*FontBBox.*')

# Suppress pdfplumber logging
import logging
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('pdfplumber').setLevel(logging.ERROR)

# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
MODEL_NAME = "cross-encoder/nli-distilroberta-base" 
FILTER_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.30
BATCH_SIZE = 4 
MAX_SEQ_LENGTH = 256 # Prevents GPU buffer overflows

keep_targets = {
    "Disney": "digital streaming, Disney+, subscribers, direct-to-consumer",
    "Adobe": "creative cloud, software subscriptions, SaaS revenue",
    "Amazon": "prime video, streaming content, digital subscriptions",
    "Netflix": "streaming service, subscribers, original content",
    "Spotify": "audio streaming, music subscriptions, podcasts",
    "PurePlayer": "digital subscription, online service, user growth"
}

theory_labels = [
    "coercive restriction and legal threat",       
    "business model adaptation and pricing",       
    "general corporate operations"                 
]

# --- SETUP ---
nltk.download('punkt', quiet=True)
dml_device = torch_directml.device()
print(f"✅ Hardware: AMD GPU via DirectML ({dml_device})")

gatekeeper = SentenceTransformer(FILTER_MODEL, device="cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(dml_device)
model.eval()

def get_metadata(filename):
    fn = filename.lower()
    year = "2020"
    y4 = re.search(r'20[2-3][0-9]', filename)
    y2 = re.search(r'(2[0-9])-q', fn)
    if y4: year = y4.group(0)
    elif y2: year = "20" + y2.group(1)

    doc_type = "Other"
    if any(x in fn for x in ["letter", "shareholder"]): doc_type = "Letter"
    elif any(x in fn for x in ["transcript", "call"]): doc_type = "Transcript"
    elif any(x in fn for x in ["10-k", "risk"]): doc_type = "RiskFactors"
    elif any(x in fn for x in ["tos", "terms"]): doc_type = "TermsOfService"
    return year, doc_type

def analyze_batch_robust(sentences, labels):
    """Batches all sentence-label pairs together for maximum GPU throughput"""
    # Create all pairs: [S1, L1], [S1, L2], [S1, L3], [S2, L1]...
    pairs = []
    for s in sentences:
        for l in labels:
            pairs.append([s, l])
    
    # Tokenize with a strict max length to prevent "Check failed" crashes
    features = tokenizer(
        pairs, 
        padding=True, 
        truncation=True, 
        max_length=MAX_SEQ_LENGTH, 
        return_tensors="pt"
    ).to(dml_device)
    
    with torch.no_grad():
        outputs = model(**features)
        # NLI Index 2 is Entailment
        scores = torch.softmax(outputs.logits, dim=1)[:, 2].cpu().tolist()
    
    # Clean up GPU memory immediately
    del features, outputs
    
    # Reconstruct results: Group scores back to sentences
    batch_results = []
    for i in range(len(sentences)):
        # Get the 3 scores for this specific sentence
        start_idx = i * len(labels)
        sent_scores = scores[start_idx : start_idx + len(labels)]
        
        best_score = max(sent_scores)
        best_label = labels[sent_scores.index(best_score)]
        batch_results.append({"label": best_label, "score": best_score})
        
    return batch_results

def extract_text_safe(pdf_path):
    """Extract text with error handling for problematic PDFs"""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pdfplumber.open(pdf_path) as pdf:
                text = " ".join([p.extract_text() or "" for p in pdf.pages])
        return text
    except Exception as e:
        # If extraction fails completely, return empty string
        return ""

def process_pdfs():
    pdf_files = [os.path.join(r, f) for r, d, f_s in os.walk(BASE_PATH) for f in f_s if f.lower().endswith('.pdf')]
    output_file = os.path.join(BASE_PATH, "Thesis_Results_Final_V5.csv")
    
    if not os.path.exists(output_file):
        pd.DataFrame(columns=['Year', 'Company', 'Doc_Type', 'Sentence', 'Label', 'Score', 'Source']).to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"Starting analysis on {len(pdf_files)} files...")
    
    for file_path in tqdm(pdf_files, ncols=80, unit='file'):
        filename = os.path.basename(file_path)
        try:
            year, doc_type = get_metadata(filename)
            company = next((c.capitalize() for c in ["disney", "adobe", "amazon", "netflix", "spotify"] if c in filename.lower()), "PurePlayer")
            
            # Text Extraction with suppressed warnings
            text = extract_text_safe(file_path)
            if not text:
                continue
            
            # Basic cleaning
            sentences = [s.strip().replace('\n', ' ') for s in nltk.tokenize.sent_tokenize(text) if 50 < len(s) < 1000]
            if not sentences: continue

            # Stage 1: Gatekeeper (Semantic Filter)
            target_profile = keep_targets.get(company, keep_targets["PurePlayer"])
            target_emb = gatekeeper.encode(target_profile, convert_to_tensor=True)
            sent_embs = gatekeeper.encode(sentences, convert_to_tensor=True)
            similarities = util.cos_sim(target_emb, sent_embs)[0]
            relevant = [sentences[i] for i, s in enumerate(similarities) if s > SIMILARITY_THRESHOLD]
            
            if not relevant: continue

            # Stage 2: GPU Analyst
            file_results = []
            for i in range(0, len(relevant), BATCH_SIZE):
                batch = relevant[i : i + BATCH_SIZE]
                preds = analyze_batch_robust(batch, theory_labels)
                
                for idx, p in enumerate(preds):
                    if p['score'] > 0.45: # Raised threshold for academic quality
                        file_results.append({
                            'Year': year,
                            'Company': company,
                            'Doc_Type': doc_type,
                            'Sentence': batch[idx],
                            'Label': p['label'],
                            'Score': round(p['score'], 4),
                            'Source': filename
                        })
            
            # Write to CSV immediately after each file
            if file_results:
                pd.DataFrame(file_results).to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            
            # Explicit Memory Management
            gc.collect()

        except Exception:
            print(f"\n❌ FATAL ERROR on file {filename}:")
            print(traceback.format_exc())
            continue # Skip bad file and keep going

    print(f"\n✅ PROCESS COMPLETE. Data in: {output_file}")

if __name__ == "__main__":
    process_pdfs()