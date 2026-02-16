import pandas as pd
excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
for sheet in xl.sheet_names:
    print(f"\nSearching categories in sheet: {sheet}")
    try:
        df = xl.parse(sheet, nrows=100)
        for col in df.columns:
            if 'category' in col.lower() or 'label' in col.lower():
                print(f"Found column '{col}' in sheet '{sheet}': {df[col].unique().tolist()}")
    except Exception as e:
        print(f"Error: {e}")
