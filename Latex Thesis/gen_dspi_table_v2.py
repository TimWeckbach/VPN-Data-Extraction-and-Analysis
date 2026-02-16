import pandas as pd
import re

excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
df = xl.parse('Sheet1')

def clean_val(val):
    if pd.isna(val) or val == '-': return None
    s = str(val).replace('$', '').replace(',', '').replace('US', '').replace('\u200b', '').strip()
    match = re.search(r'[\d\.]+', s)
    if match: return float(match.group(0))
    return None

# Target countries
target_countries = [
    'Switzerland', 'United States', 'Germany', 'United Kingdom', 'Poland', 
    'Turkey', 'Argentina', 'Brazil', 'Ukraine', 'Philippines', 'Pakistan'
]

# Find row indices for "USD Equivalent" for each country
country_usd_rows = {}
for i, row in df.iterrows():
    cell_val = str(row.iloc[0])
    if 'Equivalent' in cell_val:
        # Find the country above it
        prev_idx = i - 1
        while prev_idx >= 0:
            potential_country = str(df.iloc[prev_idx, 0])
            for c in target_countries:
                if c in potential_country:
                    country_usd_rows[c] = i
                    break
            if c in potential_country: break
            prev_idx -= 1

# Columns: Netflix(4), YT(5), Disney(6), MS365(7), Amazon(8), Adobe(9), Xbox(10), Spotify(11), Apple(12)
cols = [4, 5, 6, 8, 11, 12, 7, 9, 10, 13, 14]

us_prices = [clean_val(df.iloc[country_usd_rows['United States'], c]) for c in cols] if 'United States' in country_usd_rows else [17.99, 13.99, 13.99, 14.99, 10.99, 10.99, 6.99, 69.99, 16.99, 12.99, 12.99]
# Note: Row 26 is USA, but it doesn't have a "USD Equivalent" row below it because it IS USD.
if 'United States' not in country_usd_rows:
    # Manual check for Row 26
    country_usd_rows['United States'] = 26

print(f"USA Row: {country_usd_rows.get('United States')}")

data = []
for country in target_countries:
    row_idx = country_usd_rows.get(country)
    if row_idx is None:
        data.append([country] + ['--']*len(cols))
        continue
    
    local_row = df.iloc[row_idx]
    row_data = [country]
    for i, c in enumerate(cols):
        val = clean_val(local_row[c])
        if val is not None and us_prices[i]:
            # Handle the specific case for MS365/Adobe etc if they are already ratios? No.
            row_data.append(round(val / us_prices[i], 2))
        else:
            row_data.append('--')
    data.append(row_data)

header = ['Country', 'Netflix', 'YouTube', 'Disney', 'Amazon', 'Spotify', 'Apple', 'MS365', 'Adobe', 'Xbox', 'Nord', 'Express']
res_df = pd.DataFrame(data, columns=header)
print(res_df.to_string(index=False))
