
import pandas as pd
import os
import re

BASE_PATH = r"Quantitative DATA"
CSV_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")
BACKUP_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master.csv")

keep_targets = {
    "Disney+": "Disney+",
    "Adobe": "Adobe",
    "Amazon Prime": "Amazon Prime",
    "Netflix": "Netflix",
    "Spotify": "Spotify",
    "Youtube Premium": "Youtube Premium",
    "Apple Music": "Apple Music",
    "Microsoft": "Microsoft",
    "ExpressVPN": "ExpressVPN",
    "NordVPN": "NordVPN",
    "Amazon": "Amazon Prime",
    "PurePlayer": "Spotify" # Fallback if folder was renamed but I don't think it exists based on scan
}

def get_company_map():
    print("Scanning directory for correct Company mapping...")
    file_map = {} 
    for root, dirs, files in os.walk(BASE_PATH):
        for f in files:
            if f.lower().endswith(('.pdf', '.mp3', '.wav', '.m4a', '.mp4')):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, BASE_PATH)
                folder = rel_path.split(os.sep)[0]
                
                # Normalize
                comp = folder
                for k, v in keep_targets.items():
                    if k.lower() == folder.lower():
                        comp = v
                        break
                
                file_map[f] = comp
    return file_map

def get_doc_type(filename):
    fn = filename.lower()
    
    # 1. 10-K / Annual (Priority)
    if re.search(r'10-?k|annual|risk|form[- ]?10', fn):
        return "10-K/Annual Report"
    
    # 2. Earnings
    if re.search(r'transcript|call|earnings', fn):
        return "Earnings Call"
        
    # 3. Shareholder
    if re.search(r'letter|shareholder|commentary', fn):
        return "Shareholder Letter"
        
    # 4. Terms
    if re.search(r'tos|terms|agreement|policy', fn):
        return "Terms of Service"
        
    return "Other"

def main():
    print(f"Reading {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("File not found.")
        return

    # 1. Build Map
    comp_map = get_company_map()
    
    # 2. Update Company
    print("Updating Company and Doc_Type...")
    
    def update_row(row):
        src = row['Source']
        
        # Company
        if src in comp_map:
            row['Company'] = comp_map[src]
        elif row['Company'] == "PurePlayer":
             # Fallback if file not found but labeled PurePlayer
             # We assume it's Spotify or Netflix if we can't find it? 
             # Or mark Unknown.
             row['Company'] = "Unknown" 
             
        # Doc_Type
        row['Doc_Type'] = get_doc_type(src)
        return row
        
    df = df.apply(update_row, axis=1)
    
    # Check cleaning results
    print("\n--- POST-CLEANING STATS ---")
    print("Companies:", df['Company'].unique())
    print("Doc Types:", df['Doc_Type'].unique())
    
    count_10k_mismatch = len(df[
        (df['Source'].str.contains('10-k|10k', case=False, regex=True)) & 
        (df['Doc_Type'] != '10-K/Annual Report')
    ])
    print(f"Remaining 10-K mismatches: {count_10k_mismatch}")
    
    # 3. Save
    print(f"Saving to {CSV_FILE}...")
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    
    print(f"Saving backup to {BACKUP_FILE}...")
    df.to_csv(BACKUP_FILE, index=False, encoding='utf-8-sig')
    
    print("Done.")

if __name__ == "__main__":
    main()
