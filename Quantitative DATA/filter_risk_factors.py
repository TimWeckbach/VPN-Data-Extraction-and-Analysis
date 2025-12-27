
import pandas as pd
import os

# Paths
INPUT_CSV = r"Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
OUTPUT_CSV = r"Quantitative DATA\Thesis_Dataset_Master_RiskFactorsOnly.csv"

def filter_dataset():
    print("Loading dataset...")
    df = pd.read_csv(INPUT_CSV)
    
    # 1. Separate ToS vs 10-K
    # Doc_Type column usually helps. Or Source filename containing '10-K' or 'Annual'.
    # Inspecting previous grep, Source looks like '19-Annual-Report_Spotify.pdf' or '21-10K_Adobe.pdf'.
    
    # Filter for Annual Reports / 10-Ks
    report_mask = df['Source'].str.contains('10-K', case=False) | df['Source'].str.contains('Annual', case=False) | df['Doc_Type'].astype(str).str.contains('Report', case=False)
    
    # Split
    reports_df = df[report_mask].copy()
    tos_df = df[~report_mask].copy()
    
    print(f"Total Rows: {len(df)}")
    print(f"ToS Rows (Kept as is): {len(tos_df)}")
    print(f"Report Rows (Before Filter): {len(reports_df)}")
    
    # 2. Filter Reports for 'Risk Factor' content
    # This is tricky because the CSV is sentence-level. 
    # We look for keywords like "risk", "adversely affect", "uncertainty", "competition".
    # A cleaner heuristic is: Does the sentence likely belong to the Risk Factors section?
    # Or strict 'Risk Factor' header search if we had page numbers/sections.
    # Given we have sentences, we will use a keyword density approach or explicit 'Risk' mention.
    
    # BETTER APPROACH: 
    # The user implies "exclude everything else". 
    # Identifying the actual "Item 1A. Risk Factors" section from a bag of sentences is hard without metadata.
    # However, meaningful analysis sentences usually contain specific risk keywords.
    
    risk_keywords = ['risk', 'adversely', 'uncertainty', 'competition', 'regulation', 'breach', 'security', 'harm', 'loss', 'fail']
    
    # Function to check if sentence is "Risk-like"
    def is_risk_sentence(text):
        if not isinstance(text, str): return False
        text = text.lower()
        return any(k in text for k in risk_keywords)

    reports_df['Is_Risk'] = reports_df['Sentence'].apply(is_risk_sentence)
    
    # Keep only Risk sentences from Reports
    risk_reports_df = reports_df[reports_df['Is_Risk']]
    
    print(f"Report Rows (After Risk Keywrod Filter): {len(risk_reports_df)}")
    
    # 3. Re-combine
    final_df = pd.concat([tos_df, risk_reports_df])
    
    # Save
    final_df.drop(columns=['Is_Risk'], inplace=True, errors='ignore')
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved filtered dataset to {OUTPUT_CSV} with {len(final_df)} rows.")

if __name__ == "__main__":
    filter_dataset()
