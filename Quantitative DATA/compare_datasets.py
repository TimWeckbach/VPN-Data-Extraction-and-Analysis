import pandas as pd
import numpy as np
import os

# Paths
BASE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
OLD_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master.csv")
NEW_FILE = os.path.join(BASE_PATH, "Thesis_Dataset_Master_Redefined.csv")

def normalize_label(val):
    if pd.isna(val):
        return ""
    return str(val).strip().lower()

def main():
    print("--- Comparing Datasets ---")
    
    # Load
    try:
        df_old = pd.read_csv(OLD_FILE)
        df_new = pd.read_csv(NEW_FILE)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Ensure alignment (assuming line-by-line correspondence if same length)
    if len(df_old) != len(df_new):
        print(f"Warning: Length mismatch! Old: {len(df_old)}, New: {len(df_new)}")
        # Merge on ID if possible, but let's assume they are row-aligned for now
        # or just truncate to min length for comparison statistics
        min_len = min(len(df_old), len(df_new))
        df_old = df_old.iloc[:min_len]
        df_new = df_new.iloc[:min_len]
    
    # Extract Columns
    # Old manual label column usually named 'Label' or 'Manual_Label'
    old_col = 'Label' if 'Label' in df_old.columns else df_old.columns[4] # Guessing 5th col
    new_col = 'New_Category'
    
    y_old = df_old[old_col].apply(normalize_label)
    y_new = df_new[new_col].apply(normalize_label)
    
    # 1. Coverage Increase
    initial_filled = (y_old != "").sum()
    final_filled = (y_new != "").sum()
    print(f"\n1. DATA COMPLETENESS")
    print(f"   - Manual Labels: {initial_filled} / {len(df_old)} ({initial_filled/len(df_old):.1%})")
    print(f"   - Gemini Labels: {final_filled} / {len(df_new)} ({final_filled/len(df_new):.1%})")
    print(f"   - Increase: +{final_filled - initial_filled} rows labeled")

    # 2. Agreement (on rows where BOTH had a label)
    # Filter where both are non-empty
    valid_mask = (y_old != "") & (y_new != "")
    
    if valid_mask.sum() > 0:
        matches = (y_old[valid_mask] == y_new[valid_mask]).sum()
        total_common = valid_mask.sum()
        agreement = matches / total_common
        print(f"\n2. AGREEMENT (on {total_common} overlapping rows)")
        print(f"   - Match Rate: {agreement:.1%}")
        print(f"   - Mismatches: {total_common - matches}")
    else:
        print("\n2. AGREEMENT")
        print("   - No overlapping labels to compare.")

    # 3. Top Changes (Where did A go to B?)
    if valid_mask.sum() > 0:
        comparison = pd.DataFrame({'Old': y_old[valid_mask], 'New': y_new[valid_mask]})
        comparison = comparison[comparison['Old'] != comparison['New']]
        
        print(f"\n3. TOP RE-CLASSIFICATIONS (Old -> New)")
        if not comparison.empty:
            changes = comparison.groupby(['Old', 'New']).size().reset_index(name='Count')
            changes = changes.sort_values('Count', ascending=False).head(10)
            for idx, row in changes.iterrows():
                print(f"   - '{row['Old']}' -> '{row['New']}': {row['Count']} rows")
        else:
            print("   - No re-classifications found (Perfect match).")
            
    # 4. Distribution Shift
    print("\n4. DISTRIBUTION SHIFT (Top 5 Categories)")
    print(f"{'Category':<30} {'Old %':<10} {'New %':<10} {'Change'}")
    print("-" * 60)
    
    dist_old = y_old[y_old != ""].value_counts(normalize=True)
    dist_new = y_new[y_new != ""].value_counts(normalize=True)
    
    # Union of top keys
    all_keys = set(dist_old.head(5).index) | set(dist_new.head(5).index)
    
    # Sort by new prevalence
    sorted_keys = sorted(all_keys, key=lambda x: dist_new.get(x, 0), reverse=True)
    
    for key in sorted_keys:
        old_pct = dist_old.get(key, 0) * 100
        new_pct = dist_new.get(key, 0) * 100
        diff = new_pct - old_pct
        print(f"{key[:28]:<30} {old_pct:5.1f}%    {new_pct:5.1f}%    {diff:+5.1f}%")

if __name__ == "__main__":
    main()
