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
import whisper
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import logging

# --- SUPPRESS WARNINGS ---
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*FontBBox.*')
warnings.simplefilter("ignore")

# Suppress logging
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('pdfplumber').setLevel(logging.ERROR)
logging.getLogger('whisper').setLevel(logging.ERROR)

# --- CONFIGURATION ---
# --- CONFIGURATION ---
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
OUTPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_V7.csv")

# Models
NLI_MODEL_NAME = "cross-encoder/nli-deberta-v3-large" 
FILTER_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
WHISPER_MODEL_SIZE = "medium" # 'tiny', 'base', 'small', 'medium', 'large'

# Parameters
SIMILARITY_THRESHOLD = 0.30
BATCH_SIZE = 4 
MAX_SEQ_LENGTH = 256
CONFIDENCE_THRESHOLD = 0.45

# Targets
# Targets (Refined for Geo-Arbitrage detection)
keep_targets = {
    "Disney+": "geographic restriction, location, VPN, proxy, circumvention, account termination, country of residence",
    "Adobe": "pricing region, geographic location, service availability, export control, account blocking",
    "Amazon Prime": "geographic location, billing address, travel, abroad, VPN, location masking",
    "Netflix": "household, primary location, verification, VPN, proxy, unblocker, geographic restriction",
    "Spotify": "country change, account settings, 14 days abroad, travel, geographic license",
    "Youtube Premium": "location check, pay currency, country mismatch, VPN, ad blocker",
    "Apple Music": "country region, apple id, store front, geo-blocking, content availability",
    "Microsoft": "region setting, billing location, export laws, geo-fencing, license territory",
    "ExpressVPN": "prohibited use, copyright violation, terms of service, acceptable use", # For VPNs, we look for THEIR restrictions or disclaimers
    "NordVPN": "illegal activity, copyright, authorized use, reselling"
}

theory_labels = [
    "coercive enforcement against circumvention",       # Banning VPNs, blocking access, terminating accounts
    "geographic market segmentation",                   # Defining price/content by region (The Rule)
    "adaptive portability and travel access"            # Allowing temporary access abroad (The Innovation/Adaptation)
]

# --- SETUP ---
def setup_environment():
    print("🚀 Initializing Environment...")
    nltk.download('punkt', quiet=True)
    
    # Check device
    if torch_directml.is_available():
        device = torch_directml.device()
        print(f"✅ Hardware Accelerator: DirectML ({device})")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✅ Hardware Accelerator: CUDA ({device})")
    else:
        device = torch.device("cpu")
        print("⚠️ Hardware Accelerator: CPU (Slow)")
        
    return device

import easyocr
import numpy as np
from PIL import Image

# ... (imports)

# --- TEXT EXTRACTION ---
def extract_text_with_ocr(pdf_path, ocr_reader):
    """Fallback: Convert PDF pages to images and use OCR."""
    print(f"👁️ OCR Scanning (Image PDF): {os.path.basename(pdf_path)}...")
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    # resolution=300 is good balance. 
                    # pdfplumber.to_image requires Pillow, which is standard.
                    im = page.to_image(resolution=300).original 
                    img_np = np.array(im)
                    
                    # EasyOCR
                    # detail=0 returns just the list of strings
                    results = ocr_reader.readtext(img_np, detail=0) 
                    full_text += " ".join(results) + " "
                except Exception as e:
                    # If page rendering fails (e.g. missing dependencies), we skip page
                    pass
    except Exception as e:
        print(f"⚠️ OCR Error: {e}")
    return full_text

def extract_text_from_pdf(pdf_path, ocr_reader=None):
    """Extract text from PDF using pdfplumber, falling back to OCR if needed."""
    text = ""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                for p in pdf.pages:
                    pt = p.extract_text()
                    if pt:
                        pages_text.append(pt)
                text = " ".join(pages_text)
        
        # Fallback Check
        # 1. Text too short (Image PDF)
        # 2. Encoding issues (CID characters)
        if (len(text) < 100 or text.count('(cid:') > 50) and ocr_reader:
            print(f"⚠️ Text encoding issues detected ({text.count('(cid:')} CID chars). Switching to OCR...")
            text = extract_text_with_ocr(pdf_path, ocr_reader)
            
    except Exception as e:
        print(f"⚠️ PDF Error ({os.path.basename(pdf_path)}): {str(e)[:100]}")
    return text

def extract_text_from_audio(audio_path, whisper_model):
    """Transcribe audio using Whisper."""
    print(f"🎤 Transcribing: {os.path.basename(audio_path)}...")
    try:
        # Whisper handles format conversion internally via ffmpeg
        result = whisper_model.transcribe(audio_path, fp16=False) # fp16=False for CPU/DirectML compatibility safety
        return result['text']
    except Exception as e:
        print(f"⚠️ Audio Error ({os.path.basename(audio_path)}): {str(e)[:100]}")
        return ""

# --- PROCESSING ---
def get_metadata(filename):
    fn = filename.lower()
    
    # 1. Year Extraction
    year = "2020" # Default
    # Look for 202x
    y4 = re.search(r'20[1-3][0-9]', filename)
    # Look for YY-Qx or YY-Shareholder
    y2 = re.search(r'\b(19|2[0-5])[-_]', filename)
    
    if y4: 
        year = y4.group(0)
    elif y2: 
        year = "20" + y2.group(1)

    # 2. Doc Type
    doc_type = "Other"
    if any(x in fn for x in ["letter", "shareholder", "commentary"]): doc_type = "Shareholder Letter"
    elif any(x in fn for x in ["transcript", "call", "earnings"]): doc_type = "Earnings Call"
    elif any(x in fn for x in ["10-k", "risk", "annual"]): doc_type = "10-K/Annual Report"
    elif any(x in fn for x in ["tos", "terms", "user agreement"]): doc_type = "Terms of Service"
    
    return year, doc_type

def get_company(file_path):
    """
    Extract company name from the directory structure relative to BASE_PATH.
    Shape: BASE_PATH / CompanyName / ... / file
    """
    try:
        # Get relative path from base
        rel_path = os.path.relpath(file_path, BASE_PATH)
        # The first component of the relative path is the company folder
        company_folder = rel_path.split(os.sep)[0]
        
        # Check if the folder is one of our targets (exact match prefered)
        # We try to match with keys in keep_targets
        for target in keep_targets.keys():
            if target.lower() == company_folder.lower():
                return target
                
        # If not exact match found, return the folder name as is (User req: "always seperate like the folders")
        return company_folder
    except Exception:
        return "Unknown"

def analyze_batch(model, tokenizer, device, sentences, labels):
    """Run NLI model on a batch of sentences."""
    pairs = [[s, l] for s in sentences for l in labels]
    
    # Tokenize
    inputs = tokenizer(
        pairs, 
        padding=True, 
        truncation=True, 
        max_length=MAX_SEQ_LENGTH, 
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        logits = model(**inputs).logits
        # Index 2 is usually 'entailment' for NLI models, check model card if unsure. 
        # For cross-encoder/nli-distilroberta-base: 0=Contradiction, 1=Neutral, 2=Entailment
        probs = torch.softmax(logits, dim=1)[:, 2] # Get entailment score
    
    scores = probs.cpu().tolist()
    
    # Re-group
    results = []
    num_labels = len(labels)
    for i in range(len(sentences)):
        start = i * num_labels
        end = start + num_labels
        sent_scores = scores[start:end]
        
        best_score = max(sent_scores)
        best_label = labels[sent_scores.index(best_score)]
        results.append((best_label, best_score))
        
    return results

def main():
    device = setup_environment()
    
    # Load Models
    print("⏳ Loading Models...")
    gatekeeper = SentenceTransformer(FILTER_MODEL_NAME, device="cpu") # Keep on CPU usually fine
    
    tokenizer = AutoTokenizer.from_pretrained(NLI_MODEL_NAME)
    nli_model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_NAME).to(device)
    nli_model.eval()
    
    # Load Whisper
    print(f"⏳ Loading Whisper ({WHISPER_MODEL_SIZE})...")
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    
    # Initialize EasyOCR (Lazy load ideally, but let's init here to be safe)
    # We use CPU by default to avoid VRAM fight with NLI model, or GPU if RAM is plenty.
    # Given typical VRAM, let's stick to CPU heavily or check.
    # Actually, EasyOCR on GPU is much faster. Let's try GPU=True if available, else False.
    use_gpu_ocr = torch.cuda.is_available() or torch_directml.is_available() 
    # Note: EasyOCR doesn't natively support DirectML easily, usually CUDA.
    # If DirectML is the only thing, it might fallback to CPU anyway.
    print("⏳ Loading OCR Engine...")
    ocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available()) 
    
    # Initialize CSV
    if not os.path.exists(OUTPUT_FILE):
        pd.DataFrame(columns=['Year', 'Company', 'Doc_Type', 'Sentence', 'Label', 'Score', 'Source']).to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    # Gather Files
    all_files = []
    video_audio_exts = {'.mp3', '.wav', '.m4a', '.mp4'}
    pdf_files = []
    audio_files = []

    for root, dirs, files in os.walk(BASE_PATH):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            full_path = os.path.join(root, f)
            if ext == '.pdf':
                pdf_files.append(full_path)
            elif ext in video_audio_exts:
                audio_files.append(full_path)
    
    # Sort to prioritize PDFs (GPU accelerated) then Audio (CPU bound)
    files_to_process = sorted(pdf_files) + sorted(audio_files)
    
    print(f"📂 Found {len(files_to_process)} files ({len(pdf_files)} PDF, {len(audio_files)} Audio).")
    print("🚀 Starting with PDFs (GPU Accelerated)...")
    
    # Check already processed files to allow resume
    try:
        if os.path.exists(OUTPUT_FILE):
            existing_df = pd.read_csv(OUTPUT_FILE)
            if 'Source' in existing_df.columns:
                processed_files = set(existing_df['Source'].unique())
                print(f"ℹ️ {len(processed_files)} files already processed. Skipping them.")
                # Filter out processed
                files_to_process = [f for f in files_to_process if os.path.basename(f) not in processed_files]
    except:
        pass

    print(f"▶️ Processing {len(files_to_process)} remaining files...")

    # Main Loop
    for file_path in tqdm(files_to_process, ncols=100, unit='file'):
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        text = ""
        try:
            # 1. Extraction
            if ext == '.pdf':
                text = extract_text_from_pdf(file_path, ocr_reader)
            elif ext in video_audio_exts:
                # Warn user about CPU usage for audio
                tqdm.write(f"🎤 Transcribing Audio (CPU-bound): {filename}")
                text = extract_text_from_audio(file_path, whisper_model)
            
            if not text or len(text) < 50:
                # Log empty files
                with open(os.path.join(BASE_PATH, "skipped_files_log.txt"), "a") as log:
                    log.write(f"{filename}: Empty or failed extraction\n")
                continue

            # 2. Metadata
            year, doc_type = get_metadata(filename)
            company = get_company(file_path)
            
            # 3. Preprocessing
            # Simple sentence splitting
            raw_sentences = nltk.tokenize.sent_tokenize(text)
            sentences = [s.strip().replace('\n', ' ') for s in raw_sentences if 50 < len(s) < 1000]
            
            if not sentences: continue

            # 4. Gatekeeper (Semantic Filter) - CPU
            # Fallback to a generic profile if company not found in keys
            default_profile = "digital subscription, streaming, software services, user growth, revenue"
            target_profile = keep_targets.get(company, default_profile)
            
            target_emb = gatekeeper.encode(target_profile, convert_to_tensor=True)
            sent_embs = gatekeeper.encode(sentences, convert_to_tensor=True)
            
            # Cosine Sim
            cos_scores = util.cos_sim(target_emb, sent_embs)[0]
            
            # Filtering
            relevant_indices = [i for i, score in enumerate(cos_scores) if score > SIMILARITY_THRESHOLD]
            relevant_sentences = [sentences[i] for i in relevant_indices]
            
            if not relevant_sentences: continue

            # 5. NLI Analysis - GPU/DirectML
            file_results = []
            
            # Process in batches
            for i in range(0, len(relevant_sentences), BATCH_SIZE):
                batch_sents = relevant_sentences[i : i + BATCH_SIZE]
                batch_preds = analyze_batch(nli_model, tokenizer, device, batch_sents, theory_labels)
                
                for idx, (label, score) in enumerate(batch_preds):
                    if score > CONFIDENCE_THRESHOLD:
                        file_results.append({
                            'Year': year,
                            'Company': company,
                            'Doc_Type': doc_type,
                            'Sentence': batch_sents[idx],
                            'Label': label,
                            'Score': round(float(score), 4),
                            'Source': filename
                        })

            # 6. Save results
            if file_results:
                df_results = pd.DataFrame(file_results)
                # Append to CSV
                df_results.to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE) or os.stat(OUTPUT_FILE).st_size == 0, index=False, encoding='utf-8-sig')

            # Cleanup
            del sent_embs, cos_scores
            gc.collect()
            if device.type == 'cuda':
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"\n❌ FATAL ERROR on file {filename}:")
            print(traceback.format_exc())
            continue

    print(f"\n✅ PROCESS COMPLETE. Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
