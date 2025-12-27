import pandas as pd
import numpy as np
import os
from sklearn.metrics import classification_report, cohen_kappa_score, confusion_matrix

# Paths
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_BERT.csv")

def main():
    print("--- COMPARING MODELS: Gemini 3 Flash (Reference) vs BERT Zero-Shot (Candidate) ---")
    
    # Load
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Filter Valid Data
    # Both must have a non-empty, non-error label
    df = df[
        (df['New_Category'].notna()) & (df['New_Category'] != "") & (~df['New_Category'].str.contains("Error", na=False)) &
        (df['BERT_Category'].notna()) & (df['BERT_Category'] != "")
    ]
    
    y_true = df['New_Category'] # Gemini is our "Gold Standard" here
    y_pred = df['BERT_Category'] # BERT is what we are evaluating against it
    
    print(f"Data Points: {len(df)}")
    
    # 1. Overall Agreement (Accuracy)
    accuracy = (y_true == y_pred).mean()
    print(f"\n1. GLOBAL METRICS")
    print(f"   - Raw Agreement (Accuracy): {accuracy:.1%}")
    
    # 2. Cohen's Kappa (Accounts for chance agreement)
    kappa = cohen_kappa_score(y_true, y_pred)
    print(f"   - Cohen's Kappa:            {kappa:.3f} (Interpretation: {interpret_kappa(kappa)})")
    
    # 3. Mismatch Analysis
    mismatches = df[y_true != y_pred]
    print(f"   - Mismatches:               {len(mismatches)} rows ({len(mismatches)/len(df):.1%})")

    # 4. Detailed Classification Report
    print("\n4. DETAILED REPORT (Gemini as Ground Truth)")
    # Get unique labels from Gemini to ensure we cover everything, or union
    labels = sorted(list(set(y_true.unique()) | set(y_pred.unique())))
    
    # Check if we have enough data
    if len(labels) < 2:
        print("Not enough variation in data to generate detailed report.")
        return

    print(classification_report(y_true, y_pred, labels=labels, zero_division=0))
    
    # 5. Confusion Highlights (Where specifically do they disagree?)
    print("\n5. TOP CONFUSIONS (Gemini labeled X -> BERT labeled Y)")
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Find top off-diagonal elements
    confusions = []
    for i, row_label in enumerate(labels):
        for j, col_label in enumerate(labels):
            if i != j:
                count = cm[i, j]
                if count > 50: # Threshold to show only significant ones
                    confusions.append((row_label, col_label, count))
    
    confusions.sort(key=lambda x: x[2], reverse=True)
    
    for gemini_lab, bert_lab, count in confusions[:10]:
         print(f"   - Gemini said '{gemini_lab}' but BERT said '{bert_lab}': {count} times")

def interpret_kappa(k):
    if k < 0: return "Poor (Worse than chance)"
    if k <= 0.20: return "Slight"
    if k <= 0.40: return "Fair"
    if k <= 0.60: return "Moderate"
    if k <= 0.80: return "Substantial"
    return "Almost Perfect"

if __name__ == "__main__":
    main()
