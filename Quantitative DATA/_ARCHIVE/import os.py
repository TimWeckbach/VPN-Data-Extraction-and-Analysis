import os
import pdfplumber
import pandas as pd
import nltk
import re
from transformers import pipeline
from tqdm import tqdm # Lokale Version von TQDM

# --- KONFIGURATION ---

# 1. WINDOWS/MAC PFAD HIER EINTRAGEN!
# Wichtig: Nutze "/" statt "\", auch bei Windows.
# Beispiel: base_path = "C:/Users/Lukas/Google Drive/MASTER THESIS/Quantitative DATA"
base_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA" 

# --- SETUP ---

# NLTK laden
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

print("Lade BERT Modell (das dauert beim ersten Mal kurz)...")

# DEVICE EINSTELLUNG (Beschleunigung):
# device = -1  -> CPU (Sicher, aber langsam)
# device = 0   -> NVIDIA GPU (Sehr schnell)
# Für Mac M1/M2: Torch nutzt automatisch MPS wenn verfügbar, wir lassen es hier auf CPU (-1) für Stabilität, 
# außer du weißt, wie man MPS konfiguriert. CPU lokal ist meistens okay für 200 Dateien.
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
    "coercive restriction and legal threat",       # Protection
    "business model adaptation and pricing",       # Pricing
    "general corporate operations"                 # Mülleimer
]

def get_metadata_smart(filename):
    name_lower = filename.lower()
    
    # 1. FIRMA
    company = "Unknown"
    if "netflix" in name_lower: company = "Netflix"
    elif "disney" in name_lower: company = "Disney"
    elif "adobe" in name_lower: company = "Adobe"
    elif "amazon" in name_lower: company = "Amazon"
    elif "spotify" in name_lower: company = "Spotify"
    elif "youtube" in name_lower or "google" in name_lower: company = "YouTube"
    
    # 2. JAHR
    year = "2020" # Fallback
    year_match_4 = re.search(r'20[2-3][0-9]', filename)
    year_match_2 = re.search(r'(2[0-9])-Q', filename)
    
    if year_match_4:
        year = year_match_4.group(0)
    elif year_match_2:
        year = "20" + year_match_2.group(1)

    # 3. TYP
    doc_type = "Unknown"
    if "letter" in name_lower or "shareholder" in name_lower: doc_type = "Letter"
    elif "transcript" in name_lower or "call" in name_lower or "remarks" in name_lower: doc_type = "Transcript"
    elif "10-k" in name_lower or "risk" in name_lower or "sec" in name_lower: doc_type = "RiskFactors"
    elif "tos" in name_lower or "terms" in name_lower: doc_type = "TermsOfService"
        
    return year, company, doc_type

def process_single_pdf(file_path, filename):
    year, company, doc_type = get_metadata_smart(filename)
    
    profile_key = "PurePlayer"
    for key in context_profiles:
        if key.lower() == company.lower():
            profile_key = key
            break
            
    full_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: full_text += t + " "
    except:
        print(f"   ❌ Fehler bei: {filename}")
        return []

    sentences = nltk.tokenize.sent_tokenize(full_text)
    results = []

    for s in sentences:
        clean_s = s.strip().replace('\n', ' ')
        if len(clean_s) < 50: continue 
        
        relevant = True
        if profile_key != "PurePlayer":
            f_labels = [context_profiles[profile_key]["keep"], context_profiles[profile_key]["toss"]]
            f_res = classifier(clean_s, f_labels)
            if f_res['labels'][0] == context_profiles[profile_key]["toss"]:
                relevant = False
        
        if relevant:
            res = classifier(clean_s, theory_labels)
            score = res['scores'][0]
            if score > 0.4:
                results.append({
                    'Year': year,
                    'Company': company,
                    'Doc_Type': doc_type,
                    'Sentence': clean_s,
                    'Label': res['labels'][0],
                    'Score': score,
                    'Source_File': filename
                })
    return results

# --- START ---

all_data = []
pdf_files = []

# Prüfen ob Pfad existiert
if not os.path.exists(base_path):
    print(f"❌ FEHLER: Der Pfad wurde nicht gefunden: {base_path}")
    print("Bitte passe die Variable 'base_path' im Code oben an!")
    exit()

print(f"Suche PDFs in: {base_path}")
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(root, file))

print(f"Gefundene Dateien: {len(pdf_files)}")
print("Starte Analyse... (Fenster nicht schließen!)")

for file_path in tqdm(pdf_files):
    filename = os.path.basename(file_path)
    file_results = process_single_pdf(file_path, filename)
    all_data.extend(file_results)

if all_data:
    df = pd.DataFrame(all_data)
    out_excel = os.path.join(base_path, 'Masterthesis_Results_Final.xlsx')
    out_csv = os.path.join(base_path, 'Masterthesis_Results_Final.csv')
    
    df.to_excel(out_excel, index=False)
    df.to_csv(out_csv, index=False)
    print(f"\n✅ FERTIG! Gespeichert in: {out_excel}")
else:
    print("\n⚠️ Keine Daten gefunden.")