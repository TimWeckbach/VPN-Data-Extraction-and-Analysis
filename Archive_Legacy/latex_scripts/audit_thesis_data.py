import pandas as pd
import re

excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
tex_path = r'c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex'

xl = pd.ExcelFile(excel_path)
timeline_df = xl.parse('Timeline_Details')
fortress_df = xl.parse('Analysis_FortressIndex')

cat_map = {
    'Regulatory Compliance': 'Regulatory Compliance',
    'Technical Blocking': 'Technical Blocking',
    'Content Licensing': 'Content Licensing',
    'Legal Threat': 'Legal Threat',
    'Privacy/Security': 'Privacy/Security',
    'Security Risk': 'Security Risk',
    'Price Discrimination': 'Price Discrimination',
    'Legitimate Portability': 'Legitimate Portability',
    'User Workaround': 'User Workaround',
    'Account Action': 'Account Action'
}

with open(tex_path, 'r', encoding='utf-8') as f:
    tex_content = f.read()

print("--- AUDIT START ---")

# 1. Audit Fortress Index
print("\n[Audit: Fortress Index]")
fortress_tex_match = re.search(r'\\label{tab:app_fortress}.*?\\bottomrule', tex_content, re.DOTALL)
if fortress_tex_match:
    rows = re.findall(r'([\w\s\+]+)\s+&\s+([\d\.]+)\s+&', fortress_tex_match.group(0))
    for company, score in rows:
        company = company.strip()
        excel_row = fortress_df[fortress_df['Company'].str.contains(company, case=False, na=False)]
        if not excel_row.empty:
            excel_val = round(float(excel_row.iloc[0]['Fortress_Score']), 2)
            tex_val = float(score)
            if abs(excel_val - tex_val) > 0.1:
                print(f"Mismatch: {company} | Tex: {tex_val} | Excel: {excel_val}")
            else:
                print(f"Match: {company}")

# 2. Audit Evolution Charts
print("\n[Audit: Evolution Charts]")
# Find all figure blocks in main.tex
figure_blocks = re.findall(r'\\begin{figure}.*?\\end{figure}', tex_content, re.DOTALL)
for block in figure_blocks:
    caption_match = re.search(r'\\caption\{\s*([\w\s\+]+):\s*Strategic Frame Evolution', block)
    if caption_match:
        service_name = caption_match.group(1).strip()
        print(f"\nChecking: {service_name}")
        
        # Mapping for Excel lookup (Disney+ -> Disney+ in Excel)
        excel_search_name = service_name
        
        plots = re.findall(r'\\addplot.*?coordinates\s*\{\s*(.*?)\s*\};.*?\\addlegendentry\{(.*?)\}', block, re.DOTALL)
        for coords_str, category in plots:
             clean_cat = category.strip().replace('\\ ', ' ')
             excel_cat = cat_map.get(clean_cat, clean_cat)
             coords = re.findall(r'\((\d+),(\d+)\)', coords_str)
             for year, count in coords:
                 year_int = int(year)
                 count_int = int(count)
                 
                 excel_val_row = timeline_df[(timeline_df['Service'] == excel_search_name) & 
                                            (timeline_df['Year'] == year_int) & 
                                            (timeline_df['Category'] == excel_cat)]
                 
                 if not excel_val_row.empty:
                     excel_count = int(excel_val_row.iloc[0]['Count'])
                     if excel_count != count_int:
                         print(f"  Mismatch | {clean_cat} | {year} | Tex: {count_int} | Excel: {excel_count}")
                 elif count_int > 0:
                     print(f"  Missing in Excel: {service_name} | {excel_cat} | {year} | Tex Count: {count_int}")

print("\n--- AUDIT END ---")
