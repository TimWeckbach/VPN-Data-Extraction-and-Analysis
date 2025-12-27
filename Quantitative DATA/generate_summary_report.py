import pandas as pd
import os
import sys

# Functions to inspect data
def analyze_data():
    base_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
    csv_file = os.path.join(base_path, "Thesis_Dataset_Master.csv")
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    print("LOADING DATA...")
    df = pd.read_csv(csv_file)
    
    # 1. basic stats
    print(f"\n{'='*40}")
    print(f"DATASET OVERVIEW")
    print(f"{'='*40}")
    print(f"Total Sentences: {len(df)}")
    print(f"Files Processed: {df['Source'].nunique()}")
    print(f"Years Covered:   {sorted(df['Year'].unique())}")
    
    # 2. Company breakdown
    print(f"\n{'='*40}")
    print(f"OBSERVATIONS PER COMPANY")
    print(f"{'='*40}")
    print(df['Company'].value_counts())

    # 3. Label Breakdown
    print(f"\n{'='*40}")
    print(f"LABEL DISTRIBUTION (GLOBAL)")
    print(f"{'='*40}")
    print(df['Label'].value_counts(normalize=True).mul(100).round(2).astype(str) + '%')

    # 4. Coercion Analysis (The meaty part)
    # We want to see which company has the highest % of "coercive restriction"
    print(f"\n{'='*40}")
    print(f"COERCIVE RESTRICTION INTENSITY")
    print(f"{'='*40}")
    
    # Create valid pivot table
    pivot = pd.crosstab(df['Company'], df['Label'], normalize='index').mul(100).round(1)
    
    if 'coercive restriction and legal threat' in pivot.columns:
        coercive_col = pivot['coercive restriction and legal threat'].sort_values(ascending=False)
        print("Percentage of sentences labeled as 'Coercive/Legal Threat':")
        print(coercive_col)
    else:
        print("Label 'coercive restriction and legal threat' not found in results?")

    # 5. Top Coercive Sentences
    print(f"\n{'='*40}")
    print(f"TOP 5 MOST 'COERCIVE' SENTENCES")
    print(f"{'='*40}")
    coercive_df = df[df['Label'] == 'coercive restriction and legal threat'].sort_values(by='Score', ascending=False).head(5)
    
    for i, row in coercive_df.iterrows():
        print(f"[{row['Company']}] ({row['Score']}): \"{row['Sentence'][:150]}...\"")
        print("-" * 20)

    # 6. Save a summary CSV for the pivot
    output_dir = os.path.join(base_path, "_OUTPUTS")
    os.makedirs(output_dir, exist_ok=True)
    
    pivot_path = os.path.join(output_dir, "Analysis_Pivot_Company_Label.csv")
    pivot.to_csv(pivot_path)
    print(f"\n✅ Detailed pivot table saved to: {os.path.basename(pivot_path)}")

if __name__ == "__main__":
    try:
        analyze_data()
    except Exception as e:
        print(f"Analysis failed: {e}")
