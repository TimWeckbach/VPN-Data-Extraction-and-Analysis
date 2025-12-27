import os
import pdfplumber
import pandas as pd
import nltk
import re
import time
import gc # Garbage Collection
from transformers import pipeline
from tqdm import tqdm
import torch

# --- KONFIGURATION ---

# PFAD ANPASSEN!
base_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"

# Wir setzen Batch Size auf 1, aber nutzen FP16. 
# Das ist sicherer bei DirectML Memory Leaks.
BATCH_SIZE = 1 

# --- SETUP ---

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Hardware Erkennung
use_gpu = False
device = -1

try:
    import torch_directml
    # Prüfen ob DirectML verfügbar ist
    if torch_directml.is_available():
        dml_device = torch_directml.device()
        print(f"✅ AMD GPU gefunden: {dml_device}")
        use_gpu = True
        device = dml_device
    else:
        print("⚠️ DirectML installiert, aber keine GPU gefunden. Nutze CPU.")
except ImportError:
    print("⚠️ torch-directml nicht installiert. Nutze CPU.")
except Exception as e:
    print(f"⚠️ GPU Init Fehler: {e}. Nutze CPU.")

# MODELL LADEN (Mit FP16 wenn GPU aktiv)
print("Lade BERT Modell...")

try:
    if use_gpu:
        # Versuch mit FP16 (Halbe Präzision = Halber Speicher)
        classifier = pipeline("zero-shot-classification", 
                              model="facebook/bart-large-mnli", 
                              device=device, 
                              torch_dtype=torch.float16) 
        print("🚀 Modell läuft auf GPU mit FP16 (High Performance)")
    else:
        classifier = pipeline("zero-shot-classification", 
                              model="facebook/bart-large-mnli", 
                              device=-1)
        print("🐢 Modell läuft auf CPU (Stabil)")
except Exception as e:
    print(f"❌ Fehler beim Laden auf GPU: {e}")
    print("Falle zurück auf CPU...")
    use_gpu = False
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)

# --- DEFINITIONEN ---

context_profiles = {
    "Disney": {"keep": "digital streaming and dtc business", "toss": "theme parks, resorts and cruises"},
    "Adobe": {"keep": "creative cloud and digital media subscriptions", "toss": "enterprise marketing and advertising cloud"},
    "Amazon": {"keep": "prime video streaming and content", "toss": "e-commerce logistics, shipping and cloud infrastructure"},
    "Netflix": {"keep": "digital subscription business", "toss": "irrelevant boilerplate"},
    "Spotify": {"keep": "audio streaming subscription", "toss": "irrelevant boilerplate"},
    "PurePlayer": {"keep": "digital subscription business", "toss": "irrelevant boilerplate"}
}

theory_labels = [
    "coercive restriction and legal threat",       
    "business model adaptation and pricing",       
    "general corporate operations"                 
]

def get_metadata_smart(filename):
    name_lower = filename.lower()
    company = "Unknown"
    if "netflix" in name_lower: company = "Netflix"
    elif "disney" in name_lower: company = "Disney"
    elif "adobe" in name_lower: company = "Adobe"
    elif "amazon" in name_lower: company = "Amazon"
    elif "spotify" in name_lower: company = "Spotify"
    elif "youtube" in name_lower or "google" in name_lower: company = "YouTube"
    
    year = "2020" 
    year_match_4 = re.search(r'20[2-3][0-9]', filename)
    year_match_2 = re.search(r'(2[0-9])-Q', filename)
    if year_match_4: year = year_match_4.group(0)
    elif year_match_2: year = "20" + year_match_2.group(1)

    doc_type = "Unknown"
    if "letter" in name_lower or "shareholder" in name_lower: doc_type = "Letter"
    elif "transcript" in name_lower or "call" in name_lower: doc_type = "Transcript"
    elif "10-k" in name_lower or "risk" in name_lower: doc_type = "RiskFactors"
    elif "tos" in name_lower or "terms" in name_lower: doc_type = "TermsOfService"
        
    return year, company, doc_type

def analyze_sentences(sentences, labels, current_classifier):
    """Hilfsfunktion für die Analyse mit Fehlerbehandlung"""
    try:
        # Truncation=True verhindert Abstürze bei extrem langen Sätzen
        return current_classifier(sentences, labels, batch_size=BATCH_SIZE, truncation=True)
    except RuntimeError as e:
        if "out of memory" in str(e) or "allocate tensor" in str(e):
            raise MemoryError("GPU OOM")
        raise e

def process_single_pdf_robust(file_path, filename):
    year, company, doc_type = get_metadata_smart(filename)
    
    profile_key = "PurePlayer"
    for key in context_profiles:
        if key.lower() == company.lower():
            profile_key = key
            break

    # Text lesen
    full_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: full_text += t + " "
    except:
        return []

    sentences = nltk.tokenize.sent_tokenize(full_text)
    valid_sentences = []
    for s in sentences:
        clean_s = s.strip().replace('\n', ' ')
        if len(clean_s) >= 40: # Filter zu kurze
            valid_sentences.append(clean_s)
            
    if not valid_sentences:
        return []

    results = []
    
    # --- LOGIK MIT FALLBACK ---
    # Wir versuchen es auf der GPU. Wenn es knallt, machen wir DIESE Datei auf der CPU.
    
    try:
        sentences_to_analyze = []
        
        # STAGE 1 FILTER
        if profile_key != "PurePlayer":
            filter_labels = [context_profiles[profile_key]["keep"], context_profiles[profile_key]["toss"]]
            
            # Hier könnte der OOM passieren
            preds = analyze_sentences(valid_sentences, filter_labels, classifier)
            
            for i, pred in enumerate(preds):
                if pred['labels'][0] != context_profiles[profile_key]["toss"]:
                    sentences_to_analyze.append(valid_sentences[i])
        else:
            sentences_to_analyze = valid_sentences

        if not sentences_to_analyze:
            return []

        # STAGE 2 ANALYSE
        # Hier könnte auch OOM passieren
        theory_preds = analyze_sentences(sentences_to_analyze, theory_labels, classifier)

        for i, pred in enumerate(theory_preds):
            score = pred['scores'][0]
            if score > 0.4:
                results.append({
                    'Year': year,
                    'Company': company,
                    'Doc_Type': doc_type,
                    'Sentence': sentences_to_analyze[i],
                    'Label': pred['labels'][0],
                    'Score': score,
                    'Source_File': filename
                })

    except (MemoryError, RuntimeError) as e:
        print(f"\n⚠️ GPU Speicher voll bei {filename}. Schalte kurz auf CPU um...")
        # NOTFALL PLAN: CPU Pipeline nur für diese Sätze
        cpu_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)
        
        # Wiederholung auf CPU (langsam aber sicher)
        # Wir machen hier kein komplexes Filter-Batching, sondern einfache Schleife um sicher anzukommen
        for s in valid_sentences:
            # Stage 1 CPU
            relevant = True
            if profile_key != "PurePlayer":
                f_labels = [context_profiles[profile_key]["keep"], context_profiles[profile_key]["toss"]]
                res = cpu_classifier(s, f_labels)
                if res['labels'][0] == context_profiles[profile_key]["toss"]:
                    relevant = False
            
            # Stage 2 CPU
            if relevant:
                res = cpu_classifier(s, theory_labels)
                if res['scores'][0] > 0.4:
                    results.append({
                        'Year': year, 'Company': company, 'Doc_Type': doc_type,
                        'Sentence': s, 'Label': res['labels'][0], 'Score': res['scores'][0],
                        'Source_File': filename
                    })
        
        # CPU Modell sofort löschen um RAM freizugeben
        del cpu_classifier
        gc.collect()

    return results

# --- MAIN ---

if __name__ == "__main__":
    if not os.path.exists(base_path):
        print("PFAD FEHLER.")
        exit()

    pdf_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    print(f"Starte robuste Analyse von {len(pdf_files)} Dateien...")
    
    all_data = []
    
    # Loop mit Fortschrittsbalken
    for file_path in tqdm(pdf_files):
        filename = os.path.basename(file_path)
        data = process_single_pdf_robust(file_path, filename)
        all_data.extend(data)
        
        # AGGRESSIVE CLEANUP nach jeder Datei
        gc.collect() 
        if use_gpu:
            try:
                # Versuch GPU Cache zu leeren (geht bei DML oft nicht, aber wir versuchen es)
                torch.cuda.empty_cache() 
            except:
                pass

    if all_data:
        df = pd.DataFrame(all_data)
        out = os.path.join(base_path, 'Masterthesis_Results_Robust.xlsx')
        df.to_excel(out, index=False)
        print(f"\n✅ GESCHAFFT! Gespeichert: {out}")
    else:
        print("\n⚠️ Keine Daten extrahiert.")