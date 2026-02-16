import pandas as pd
import os
import re
from collections import Counter

# --- CONFIGURATION ---
BASE_PATH = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
INPUT_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")
OUTPUT_DIR = BASE_PATH

# Output Files
FILE_TIMELINE = os.path.join(OUTPUT_DIR, "Analysis_Timeline.csv")
FILE_FORTRESS = os.path.join(OUTPUT_DIR, "Analysis_FortressIndex.csv")
FILE_KEYWORDS = os.path.join(OUTPUT_DIR, "Analysis_Keywords.csv")

def main():
    print(f"Reading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    # Ensure correct column names
    if 'Category_Gemini3' not in df.columns and 'New_Category' in df.columns:
        df.rename(columns={'New_Category': 'Category_Gemini3'}, inplace=True)
    
    category_col = 'Category_Gemini3'
    if category_col not in df.columns:
        print("Error: Could not find category column.")
        return

    # --- 1. ENFORCEMENT TIMELINE ---
    print("Generating Enforcement Timeline...")
    # Filter for coercive categories
    coercive_cats = ['Technical Blocking', 'Legal Threat', 'Account Action']
    df_coercive = df[df[category_col].isin(coercive_cats)].copy()
    
    # Pivot: Index=Year, Columns=Service, Values=Count
    timeline = df_coercive.groupby(['Year', 'Company']).size().unstack(fill_value=0)
    timeline.to_csv(FILE_TIMELINE)
    print(f" - Saved to {FILE_TIMELINE}")

    # --- 2. FORTRESS INDEX ---
    print("Generating Fortress Index...")
    # Exclude General Terms for the denominator? 
    # Index = (Coercive Count / Total Strategic Count) * 100
    df_strategic = df[df[category_col] != 'General Terms']
    
    total_strategic = df_strategic.groupby('Company').size()
    coercive_counts = df_coercive.groupby('Company').size()
    
    fortress_index = (coercive_counts / total_strategic * 100).fillna(0).sort_values(ascending=False)
    fortress_df = fortress_index.reset_index(name='Fortress_Score')
    fortress_df.to_csv(FILE_FORTRESS, index=False)
    print(f" - Saved to {FILE_FORTRESS}")

    # --- 3. BLOCKING KEYWORDS ---
    print("Generating Top Blocking Keywords...")
    df_blocking = df[df[category_col] == 'Technical Blocking'].copy()
    
    # Simple tokenizer
    all_text = " ".join(df_blocking['Sentence'].dropna().astype(str)).lower()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
    
    # Stopwords (Basic list)
    stopwords = set(['the', 'and', 'that', 'for', 'you', 'with', 'are', 'this', 'our', 'may', 'use', 'service', 'services', 'not', 'your', 'from', 'content', 'access', 'which', 'such'])
    filtered_words = [w for w in words if w not in stopwords]
    
    common = Counter(filtered_words).most_common(30)
    keywords_df = pd.DataFrame(common, columns=['Keyword', 'Frequency'])
    keywords_df.to_csv(FILE_KEYWORDS, index=False)
    print(f" - Saved to {FILE_KEYWORDS}")

if __name__ == "__main__":
    main()
