
import pandas as pd
import re
import sys
import os

OUTPUT_FILE = 'Thesis_Dataset_Master_RiskFactorsOnly.csv'

def extract_risk_factors(input_file):
    print(f"Reading {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    # Sort to ensure order
    if 'Year' in df.columns and 'Company' in df.columns:
        df = df.sort_values(by=['Company', 'Year'])

    extracted_rows = []
    
    grouped = df.groupby(['Company', 'Year'])
    
    stats = []

    for (company, year), group in grouped:
        print(f"Processing {company} {year} ({len(group)} rows)...")
        
        group = group.reset_index(drop=False) # Keep original index if needed, but we processed sequentially
        sentences = group['Sentence'].astype(str).tolist()
        
        start_idx = -1
        end_idx = -1
        
        # Regex patterns
        # Start: Item 1A or Risk Factors (as a headline)
        # We look for "Item 1A" specifically.
        start_pattern = re.compile(r'item\s*1a\.?', re.IGNORECASE)
        start_pattern_strict = re.compile(r'^item\s*1a\.?', re.IGNORECASE)
        
        # End: Item 1B or Item 2
        end_pattern = re.compile(r'item\s*(1b|2)\.?', re.IGNORECASE)
        
        # Find start
        # Strategy: Find all matches. The real section is usually NOT the first match if TOC exists.
        # But TOC entries usually have "......" or "Page".
        # If we can't distinguish, usually the Risk Factors section is the longest text block between markers.
        
        matches_start = []
        for i, s in enumerate(sentences):
            if start_pattern.search(s):
                # Check if it looks like TOC
                if "....." in s or re.search(r'\d+$', s.strip()): # Ending in number -> likely TOC page number
                    continue
                matches_start.append(i)
        
        # If no explicit "Item 1A", look for "Risk Factors" as a short sentence
        if not matches_start:
             for i, s in enumerate(sentences):
                if "risk factors" in s.lower():
                     if len(s) < 50: # Short headline
                         matches_start.append(i)

        if not matches_start:
            print(f"  WARNING: No 'Item 1A' start marker found for {company} {year}")
            continue
            
        # Strategy: For each potential start, look for the nearest subsequent end marker.
        # Calc length. Pick the start-end pair with reasonable length (e.g. > 10 sentences).
        
        best_start = -1
        best_end = -1
        max_len = 0
        
        for s_idx in matches_start:
            # Find closest end after s_idx
            e_idx = -1
            for i in range(s_idx + 1, len(sentences)):
                if end_pattern.search(sentences[i]):
                    e_idx = i
                    break
            
            # If no end marker found, maybe it goes to end of doc (unlikely) or next Item 2
            if e_idx == -1:
                # search for "Item 2" explicitly if 1B was missed
                item2 = re.compile(r'item\s*2\.?', re.IGNORECASE)
                for i in range(s_idx + 1, len(sentences)):
                    if item2.search(sentences[i]):
                        e_idx = i
                        break
            
            if e_idx != -1:
                length = e_idx - s_idx
                if length > max_len:
                    max_len = length
                    best_start = s_idx
                    best_end = e_idx
        
        if best_start != -1:
            print(f"  Found section: lines {best_start} to {best_end} (Length: {max_len})")
            # Extract
            # note: s_idx includes the header "Item 1A". We usually want the content. 
            # But the user said "under the headline". So maybe exclude the headline?
            # Or keep it. I'll keep it to be safe, or start + 1.
            # Let's keep from best_start.
            
            # Add to extracted
            subset = group.iloc[best_start:best_end]
            extracted_rows.append(subset)
            stats.append({'Company': company, 'Year': year, 'Count': len(subset)})
        else:
            print(f"  WARNING: No valid section found for {company} {year}")

    if extracted_rows:
        result_df = pd.concat(extracted_rows, ignore_index=True)
        # Drop the 'index' column if created by reset_index
        if 'index' in result_df.columns:
            result_df = result_df.drop(columns=['index'])
            
        print(f"Saving {len(result_df)} rows to {OUTPUT_FILE}")
        result_df.to_csv(OUTPUT_FILE, index=False)
        
        # Display stats
        stats_df = pd.DataFrame(stats)
        print("\nExtraction Stats:")
        print(stats_df)
    else:
        print("No rows extracted.")

if __name__ == "__main__":
    extract_risk_factors('Thesis_Dataset_Master.csv')
