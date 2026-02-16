import pandas as pd
excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
sheets = ['Qual_Master', 'Timeline_Details', 'Thesis_Dataset_Master_BERT']
for sheet in sheets:
    if sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet)
        for col in df.columns:
            if 'category' in col.lower() or 'label' in col.lower() or 'new_category' in col.lower():
                print(f"Unique values in '{col}': {df[col].unique().tolist()}")
