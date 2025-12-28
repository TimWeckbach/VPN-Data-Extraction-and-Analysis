import pandas as pd
import os
import datetime

# --- CONFIGURATION ---
BASE_PATH = r"Quantitative DATA"
DSPI_FILE = os.path.join(BASE_PATH, "dspi_raw_data.csv")
QUAL_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")
OUTPUT_DIR = BASE_PATH

def process_qualitative_stats(df_qual):
    # Normalize Columns
    if 'Service Name' in df_qual.columns:
        df_qual = df_qual.rename(columns={'Service Name': 'Service'})
    if 'Company' in df_qual.columns:
        df_qual = df_qual.rename(columns={'Company': 'Service'})
    if 'Target Year' in df_qual.columns:
        df_qual = df_qual.rename(columns={'Target Year': 'Year'})
        
    # Filter out boilerplate
    # Filter out boilerplate
    cat_col = 'Category_Gemini3'
    if cat_col not in df_qual.columns:
         if 'New_Category' in df_qual.columns:
             cat_col = 'New_Category' # Fallback
         else:
             print("Critical Error: Classification column missing.")
             return None, None, None

    df_clean = df_qual[df_qual[cat_col] != 'General Terms'].copy()
    
    # 1. Frequency per Category (Overview)
    cat_counts = df_clean[cat_col].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Wait_Frequency']
    cat_counts['Percent'] = (cat_counts['Wait_Frequency'] / len(df_clean) * 100).round(2)
    
    # 2. Timeline (Category per Year)
    if 'Year' in df_clean.columns:
        timeline = df_clean.groupby(['Year', cat_col]).size().unstack(fill_value=0)
        # Normalize
        timeline_norm = timeline.div(timeline.sum(axis=1), axis=0) * 100
    else:
        timeline_norm = pd.DataFrame()

    # 3. Service Distribution (Normalized Ratios per Service)
    service_group = df_qual.groupby(['Service', cat_col]).size().unstack(fill_value=0)
    service_ratios = service_group.div(service_group.sum(axis=1), axis=0) * 100
    service_ratios = service_ratios.round(2)

    # 4. Detailed Faceted Timeline (Year, Service, Category, Percentage)
    df_counts = df_qual.groupby(['Year', 'Service', cat_col]).size().reset_index(name='Count')
    df_totals = df_counts.groupby(['Year', 'Service'])['Count'].transform('sum')
    df_counts['Percentage'] = (df_counts['Count'] / df_totals) * 100
    df_counts = df_counts.round(2)
        
    return cat_counts, timeline_norm, df_qual, service_ratios, df_counts # Return full df with normalized cols

def main():
    print("--- GENERATING CSV EXPORTS FOR GOOGLE SHEETS ---")
    
    # 1. DSPI Data
    if os.path.exists(DSPI_FILE):
        print(f"Exporting {DSPI_FILE}...")
        # It's already a CSV, but let's ensure it's clean
        dspi_df = pd.read_csv(DSPI_FILE)
        dspi_df.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_DSPI.csv"), index=False)
    
    # 2. Qualitative Data
    if os.path.exists(QUAL_FILE):
        print(f"Processing {QUAL_FILE}...")
        qual_df = pd.read_csv(QUAL_FILE)
        
        counts, timeline, qual_df_norm, service_stats, timeline_details = process_qualitative_stats(qual_df)
        
        if counts is not None:
            counts.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Qual_Counts.csv"), index=False)
            timeline.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Qual_Timeline.csv")) # Index (Year) is needed
            service_stats.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Service_Stats.csv")) # Index (Service) is needed
            timeline_details.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Timeline_Details.csv"), index=False)
            
            # Use detected column for raw data export
            cat_col_src = 'Category_Gemini3' if 'Category_Gemini3' in qual_df_norm.columns else 'New_Category'
            qual_df_norm.rename(columns={cat_col_src: 'New_Category'}, inplace=True)
            
            # Rename to standard for output
            cols = ['Year', 'Service', 'Sentence', 'New_Category', 'Confidence']
            if 'Confidence_Score' in qual_df_norm.columns:
                cols = ['Year', 'Service', 'Sentence', 'New_Category', 'Confidence_Score']

            # Filter valid columns only
            valid_cols = [c for c in cols if c in qual_df_norm.columns]
            qual_df_norm[valid_cols].to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Qual_Raw.csv"), index=False)
            
            # 3. Correlation Data
            if os.path.exists(DSPI_FILE):
                print("Generating Correlation Data...")
                dspi_df = pd.read_csv(DSPI_FILE)
                # Ensure Service col matches
                if 'Service Name' in dspi_df.columns: dspi_df.rename(columns={'Service Name': 'Service'}, inplace=True)
                
                # RECALCULATE DSPI for Stats (Because 'DSPI' col is now a formula string!)
                # We added 'Price_USD_Static' in process_google_sheet_data.py for this exact purpose.
                # If it exists, use it. If not (old data), fallback to 'Price_USD'.
                
                if 'Price_USD_Static' in dspi_df.columns:
                     # Calculate Baseline again or assume it is handled?
                     # Let's handle it robustly.
                     # Baseline = USA Price
                     us_prices = dspi_df[dspi_df['Country'].isin(['United States', 'USA'])].set_index('Service')['Price_USD_Static'].to_dict()
                     
                     def get_dspi_val(row):
                         base = us_prices.get(row['Service'])
                         if base and base > 0:
                             return row['Price_USD_Static'] / base
                         return None
                         
                     dspi_df['DSPI_Value'] = dspi_df.apply(get_dspi_val, axis=1)
                else:
                     # Old format fallback
                     dspi_df['DSPI_Value'] = pd.to_numeric(dspi_df['DSPI'], errors='coerce')

                # 1. Price Discrim (StdDev of DSPI Value)
                dspi_std = dspi_df.groupby('Service')['DSPI_Value'].std().reset_index(name='Price_Discrimination_Score')
                
                # 2. Enforcement Intensity
                # We renamed the column to 'New_Category' above, so use that.
                export_cat_col = 'New_Category'
                
                total_sentences = qual_df_norm.groupby('Service').size()
                enforcement_sentences = qual_df_norm[qual_df_norm[export_cat_col].isin(['Technical Blocking', 'Legal Threat', 'Account Action'])].groupby('Service').size()
                intensity = (enforcement_sentences / total_sentences * 100).fillna(0).reset_index(name='Enforcement_Intensity_Percent')
                
                # Merge
                corr_df = pd.merge(dspi_std, intensity, on='Service', how='inner')
                corr_df.to_csv(os.path.join(OUTPUT_DIR, "Sheets_Import_Correlation.csv"), index=False)

    print("\nSUCCESS. CSV Files Generated.")
    print("Please import these files into your Google Sheet.")

if __name__ == "__main__":
    main()
