import pandas as pd
import os

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\tables\Digital Services Price Index (DSPI).xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print(f"File: {os.path.basename(file_path)}")
    print(f"Sheet Names: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        try:
            df = pd.read_excel(file_path, sheet_name=sheet, nrows=20, header=None)
            print(df.to_string())
        except Exception as e:
            print(f"Error reading sheet {sheet}: {e}")

except Exception as e:
    print(f"Error opening Excel file: {e}")
