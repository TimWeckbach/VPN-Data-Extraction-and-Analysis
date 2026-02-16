import pandas as pd
import os

FILE_PATH = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"

def fix_dataset():
    print(f"Loading {FILE_PATH}...")
    try:
        df = pd.read_csv(FILE_PATH)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Check columns
    print(f"Columns: {df.columns.tolist()}")
    target_col = 'Category_Gemini3'
    if target_col not in df.columns:
        print(f"Column {target_col} not found!")
        # Fallback check
        if 'New_Category' in df.columns:
            target_col = 'New_Category'
            print(f"Using {target_col} instead.")
        else:
            print("Cannot find category column.")
            return

    changes = 0

    # Fix 1: "different country" -> Regulatory Compliance
    # Condition: Sentence contains "If you are located in a different country from the applicable Adobe entity" AND Category is "Price Discrimination"
    mask1 = df['Sentence'].str.contains("If you are located in a different country", case=False, na=False) & \
            (df[target_col] == "Price Discrimination")
    
    count1 = mask1.sum()
    if count1 > 0:
        print(f"Found {count1} rows for 'different country' fix.")
        df.loc[mask1, target_col] = "Regulatory Compliance"
        changes += count1

    # Fix 2: "digital rights management" -> Content Licensing
    mask2 = df['Sentence'].str.contains("Our digital content offerings depend in part on effective digital rights management", case=False, na=False) & \
            (df[target_col] != "Content Licensing")
    
    count2 = mask2.sum()
    if count2 > 0:
        print(f"Found {count2} rows for 'DRM' fix.")
        df.loc[mask2, target_col] = "Content Licensing"
        changes += count2

    if changes > 0:
        print(f"Applying {changes} changes and saving...")
        df.to_csv(FILE_PATH, index=False)
        print("File saved.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    fix_dataset()
