import pandas as pd
import os

file_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
output_dir = r'c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\SSoT_CSVs'
os.makedirs(output_dir, exist_ok=True)

xl = pd.ExcelFile(file_path)
for sheet in xl.sheet_names:
    if any(x in sheet for x in ['Analysis', 'Qual', 'Terms', 'Evolution', 'Stats', 'Dashboard', 'Model']):
        sanitized_name = sheet.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        df = xl.parse(sheet)
        df.to_csv(os.path.join(output_dir, f'{sanitized_name}.csv'), index=False)
        print(f'Exported {sheet} to {sanitized_name}.csv')
