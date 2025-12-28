
import os
import pandas as pd
from collections import defaultdict

BASE_PATH = r"Quantitative DATA"
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
    "Amazon": "Amazon Prime" # Fix mismatch if any
}

def scan_files():
    file_map = defaultdict(list) # filename -> list of [full_path, company]
    
    print(f"Scanning {BASE_PATH}...")
    for root, dirs, files in os.walk(BASE_PATH):
        for f in files:
            if f.lower().endswith(('.pdf', '.mp3', '.wav', '.m4a', '.mp4')):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, BASE_PATH)
                company_folder = rel_path.split(os.sep)[0]
                
                # Normalize Company
                company = company_folder
                for k, v in keep_targets.items():
                    if k.lower() == company_folder.lower():
                        company = v
                        break
                
                file_map[f].append((full_path, company))
                
    return file_map

def check_duplicates(file_map):
    duplicates = {k: v for k, v in file_map.items() if len(v) > 1}
    if duplicates:
        print(f"WARNING: Found {len(duplicates)} duplicate filenames!")
        for k, v in list(duplicates.items())[:5]:
            print(f"  {k}: {len(v)} copies ({[x[1] for x in v]})")
    else:
        print("No duplicate filenames found. Safe to map by filename.")
    return len(duplicates)

if __name__ == "__main__":
    fmap = scan_files()
    check_duplicates(fmap)
