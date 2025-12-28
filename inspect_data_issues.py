
import pandas as pd
import os

try:
    df = pd.read_csv(r"Quantitative DATA\Thesis_Dataset_Master_Redefined.csv")
    
    print("--- UNIQUE COMPANIES ---")
    print(df['Company'].unique())
    
    print("\n--- 'Pureplayer' SAMPLES ---")
    pureplayer_df = df[df['Company'] == 'Pureplayer']
    if not pureplayer_df.empty:
        print(pureplayer_df[['Source', 'Company']].head(5))
        # Print a source file path to help locate it
        print(f"Sample Source: {pureplayer_df.iloc[0]['Source']}")
    else:
        print("No 'Pureplayer' found in Company column.")
        
    print("\n--- DOC TYPES ---")
    print(df['Doc_Type'].unique())
    
    print("\n--- 10-K MISMATCHES ---")
    # Rows where filename has 10-K but Doc_Type is not 10-K
    # Check case-insensitive
    mismatch = df[
        (df['Source'].str.contains('10-k', case=False, na=False) | 
         df['Source'].str.contains('10k', case=False, na=False)) & 
        (~df['Doc_Type'].str.contains('10-K', case=False, na=False))
    ]
    
    if not mismatch.empty:
        print(f"Found {len(mismatch)} potential 10-K mismatches.")
        print(mismatch[['Source', 'Doc_Type']].head(10))
    else:
        print("No obvious 10-K mismatches found.")
        
except Exception as e:
    print(f"Error: {e}")
