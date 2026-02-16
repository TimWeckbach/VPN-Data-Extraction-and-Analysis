import pandas as pd
excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
print(f"Sheet names: {xl.sheet_names}")
for sheet in xl.sheet_names:
    try:
        df = xl.parse(sheet, nrows=2)
        print(f"\n--- Sheet: {sheet} ---")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sample row 1: {df.iloc[0].to_dict() if not df.empty else 'Empty'}")
    except Exception as e:
        print(f"Error reading {sheet}: {e}")
