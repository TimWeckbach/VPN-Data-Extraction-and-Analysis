import pandas as pd
excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
for s in xl.sheet_names:
    try:
        df = xl.parse(s)
        print(f"Sheet: {s} | Shape: {df.shape}")
    except Exception as e:
        print(f"Sheet: {s} | Error: {e}")
