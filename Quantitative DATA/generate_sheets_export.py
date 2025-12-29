import pandas as pd
import os
import numpy as np

# --- CONFIGURATION ---
BASE_PATH = r"Quantitative DATA"
QUAL_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")
DSPI_FILE = os.path.join(BASE_PATH, "dspi_raw_data.csv")
OUTPUT_DIR = BASE_PATH # Save directly to Quantitative DATA to match upload pipeline expectations

def process_qualitative_stats():
    print(f"Reading {QUAL_FILE}...")
    try:
        df = pd.read_csv(QUAL_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find {QUAL_FILE}")
        return

    # --- 1. Column Mapping & Cleanup ---
    # Check which confidence column to use. 'Score' seems to have actual values.
    # 'Confidence_Score' (last col) seems to be 0.0 based on inspection.
    # We will prioritize 'Score' if it exists and has non-zero mean.
    
    use_score_col = 'Score'
    if 'Score' in df.columns:
        print(f"Using 'Score' column for Confidence (Mean: {df['Score'].mean():.4f})")
        df['Confidence_Score'] = df['Score'] # Overwrite or create
    
    # Map columns to standard names
    # Expected: Year, Service, Sentence, New_Category, Confidence_Score, Doc_Type
    col_map = {
        'Company': 'Service',
        'Category_Gemini3': 'New_Category',
        'Category': 'New_Category', # Fallback
        'Doc_Type': 'Doc_Type'
    }
    df.rename(columns=col_map, inplace=True)
    
    # Ensure columns exist
    required_cols = ['Year', 'Service', 'Sentence', 'New_Category', 'Confidence_Score', 'Doc_Type']
    for c in required_cols:
        if c not in df.columns:
            print(f"Warning: Column '{c}' missing. Creating empty.")
            df[c] = ""
            
    df_clean = df[required_cols].copy()
    
    # --- 2. Forward Fill Logic (Imputation) ---
    # Logic: For each Service + Year, if data exists, keep it. 
    # If a year is missing (between start and 2025), we assume the LAST known document's rules apply.
    # However, copying 25k sentences for every missing year is huge. 
    # Just repeating the "Category" stats might be enough for aggregate charts, 
    # BUT the user wants "Qual_Raw" to be "Forward-Filled" in the sheet?
    # Actually, the user asked for "forward-fill logic" previously. 
    # If we replicate ALL sentences for missing years, the dataset explodes (25k * 5 years = 125k rows).
    # Google Sheets limit is 10M cells, so 125k rows * 6 cols = 750k cells. This is Acceptable.
    
    print("Applying Forward-Fill Logic...")
    
    # Get all years and services
    all_years = range(2018, 2026) # 2018 to 2025
    services = df_clean['Service'].unique()
    
    filled_dfs = []
    
    for service in services:
        srv_data = df_clean[df_clean['Service'] == service].copy()
        if srv_data.empty:
            continue
            
        # Find years active
        active_years = sorted(srv_data['Year'].unique())
        if not active_years:
            continue
            
        # Start from the first year present? Or always 2018?
        # Let's assume we fill forward from the first year we have data.
        min_year = min(active_years)
        
        # Sort by year
        srv_data = srv_data.sort_values('Year')
        
        # We need to iterate 2018 to 2025
        # If year < min_year, maybe no data? Or fill backward? No, usually forward fill.
        
        # Logic: Valid document in Y1. If Y2 is missing, copy Y1 active document sentences to Y2.
        # If Y2 has a new document, use Y2.
        
        # Get the latest "state" (set of sentences)
        last_state = None
        
        for yr in all_years:
            if yr < min_year:
                # Optional: Skip years before first data point
                continue
                
            if yr in active_years:
                # We have data, update state
                current_data = srv_data[srv_data['Year'] == yr].copy()
                last_state = current_data
                filled_dfs.append(current_data)
            else:
                # Missing year. Use last_state
                if last_state is not None:
                    # Create copy of last state, update Year
                    filled_data = last_state.copy()
                    filled_data['Year'] = yr
                    # Mark distinct? Maybe not, just fill.
                    filled_dfs.append(filled_data)
                # If no last_state yet, we can't fill (validly missing start)

    df_filled = pd.concat(filled_dfs, ignore_index=True)
    print(f"Original Rows: {len(df_clean)}, Filled Rows: {len(df_filled)}")
    
    # Save Qual_Raw
    out_file = os.path.join(OUTPUT_DIR, "Sheets_Import_Qual_Raw.csv")
    df_filled.to_csv(out_file, index=False)
    print(f"Saved {out_file}")
    
    return df_filled

def process_dspi():
    print(f"Processing DSPI from {DSPI_FILE}...")
    try:
        dspi_df = pd.read_csv(DSPI_FILE)
    except FileNotFoundError:
        print(f"Error: {DSPI_FILE} not found.")
        return

    # Basic cleanup if needed
    # Ensure DSPI_Value is numeric
    if 'DSPI' in dspi_df.columns:
        dspi_df['DSPI'] = pd.to_numeric(dspi_df['DSPI'], errors='coerce')
        
    out_file = os.path.join(OUTPUT_DIR, "Sheets_Import_DSPI.csv")
    dspi_df.to_csv(out_file, index=False)
    print(f"Saved {out_file}")

def main():
    print("--- starting export generation ---")
    process_qualitative_stats()
    process_dspi()
    print("--- completed ---")

if __name__ == "__main__":
    main()
