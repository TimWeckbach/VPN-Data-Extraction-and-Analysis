# 1. Installiere notwendige Bibliotheken
# pdfplumber ist super, um Text aus PDFs zu holen
!pip install transformers pdfplumber pandas openpyxl

import os
import pdfplumber
import pandas as pd
from transformers import pipeline
from google.colab import drive

# 2. Verbinde dich mit Google Drive
drive.mount('/content/drive')

# 3. Lade das BERT Modell (Zero-Shot)
print("Lade Modell...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Deine Theorie-Kategorien (Labels)
labels = [
    "coercive restriction and legal threat",  # Coercive
    "business model adaptation and pricing",  # Adaptive
    "general corporate information"           # Rauschen (Noise)
]

# 4. Funktion: PDF Text extrahieren und in Sätze zerlegen
def process_pdf(file_path):
    sentences = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Einfaches Splitten am Punkt.
                # Für Profi-Level könnte man 'nltk' nutzen, aber das hier reicht.
                raw_sentences = text.split('.')
                for s in raw_sentences:
                    clean_s = s.strip()
                    # Filter: Nur Sätze nehmen, die lang genug sind (keine Seitenzahlen)
                    if len(clean_s) > 30:
                        sentences.append(clean_s)
    return sentences

# 5. Der Haupt-Loop (Hier passiert die Magie)
pdf_folder = '/content/drive/MyDrive/thesis_pdfs' # Pfad zu deinem Ordner
results_data = []

# Gehe durch alle Dateien im Ordner
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        print(f"Analysiere Datei: {filename}...")
        file_path = os.path.join(pdf_folder, filename)
        
        # Text holen
        sentences = process_pdf(file_path)
        
        # WICHTIG: Performance-Trick
        # Shareholder Letters sind lang. Wenn wir JEDEN Satz analysieren, dauert es Stunden.
        # Wir filtern vorher nach relevanten Keywords.
        keywords = ["vpn", "proxy", "account", "sharing", "password", "price", 
                    "cost", "revenue", "tier", "plan", "member", "growth", "access"]
        
        relevant_sentences = [s for s in sentences if any(k in s.lower() for k in keywords)]
        
        print(f" -> Gefundene relevante Sätze: {len(relevant_sentences)}")

        # BERT Analyse für jeden Satz
        if relevant_sentences:
            # Das Modell arbeitet
            predictions = classifier(relevant_sentences, labels)
            
            for i, pred in enumerate(predictions):
                # Wir speichern: Datei, Satz, Gewinner-Label, Score
                top_label = pred['labels'][0]
                top_score = pred['scores'][0]
                
                results_data.append({
                    "Filename": filename,
                    "Sentence": relevant_sentences[i],
                    "Label": top_label,
                    "Score": top_score
                })

# 6. Speichern als Excel
print("Speichere Ergebnisse...")
df = pd.DataFrame(results_data)
df.to_excel("/content/drive/MyDrive/thesis_bert_results.xlsx", index=False)
print("Fertig! Datei liegt in deinem Drive.")