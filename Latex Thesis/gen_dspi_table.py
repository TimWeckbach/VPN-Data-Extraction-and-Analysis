import pandas as pd
import re

excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
df = xl.parse('Sheet1')

country_rows = {
    'Switzerland': 23,
    'United States': 26,
    'Germany': 42,
    'United Kingdom': 53,
    'Poland': 66,
    'Turkey': 85,
    'Argentina': 106,
    'Brazil': 122,
    'Ukraine': 138,
    'Philippines': 145,
    'Pakistan': 168
}

def clean_val(val):
    if pd.isna(val): return None
    s = str(val).replace('$', '').replace(',', '').replace('US', '').replace('\u200b', '').strip()
    match = re.search(r'[\d\.]+', s)
    if match: return float(match.group(0))
    return None

cols = [4, 5, 6, 8, 11, 12, 7, 9, 10, 13, 14]
# Netflix, YT, Disney, Amazon, Spotify, Apple, MS365, Adobe, Xbox, Nord, Express

us_row = country_rows['United States']
us_prices = [clean_val(df.iloc[us_row, c]) for c in cols]

data = []
for country, row_idx in country_rows.items():
    local_row = df.iloc[row_idx]
    row_data = [country]
    for i, c in enumerate(cols):
        val = clean_val(local_row[c])
        if val is not None and us_prices[i]:
            row_data.append(round(val / us_prices[i], 2))
        else:
            row_data.append('--')
    data.append(row_data)

header = ['Country', 'Netflix', 'YouTube', 'Disney', 'Amazon', 'Spotify', 'Apple', 'MS365', 'Adobe', 'Xbox', 'Nord', 'Express']
res_df = pd.DataFrame(data, columns=header)
print(res_df.to_string(index=False))
