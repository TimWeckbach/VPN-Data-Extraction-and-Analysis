import pandas as pd
import re

excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
df = xl.parse('Sheet1')

def clean_val(val):
    if pd.isna(val): return None
    s = str(val).replace('$', '').replace(',', '').replace('US', '').strip()
    match = re.search(r'[\d\.]+', s)
    if match: return float(match.group(0))
    return None

# Mapping rows (assuming row indices from previous inspection)
country_rows = {
    'Switzerland': 23,
    'USA': 26, # Row 26 is United States
    'Germany': 42,
    'UK': 53,
    'Poland': 66,
    'Turkey': 85,
    'Argentina': 106,
    'Brazil': 122,
    'Ukraine': 138,
    'Philippines': 145, # This one was odd
    'Pakistan': 168
}

us_netflix = 17.99
us_yt = 13.99

print("Country | Netflix | YT | Disney | Amazon | Spotify | Apple")
print("-" * 60)

for country, idx in country_rows.items():
    # Columns: Netflix(4), YT(5), Disney(6), Microsoft(7), Amazon(8), Adobe(9), Xbox(10), Spotify(11), Apple(12)
    # Correcting column indices based on previous df.columns output:
    # ['Price of', 'Unnamed: 1', 'Unnamed: 2', '2020-2025', 'Netflix', 'Youtube Premium', 'Disney Plus', 'Microsoft 365', 'Amazon Prime', 'Adobe Creative Cloud', 'Xbox Game Pass', 'Spotify', 'Apple Music', 'NordVPN', 'ExpressVPN']
    # Index: 4=Netflix, 5=YT, 6=Disney, 7=Microsoft, 8=Amazon, 9=Adobe, 10=Xbox, 11=Spotify, 12=Apple
    
    n = clean_val(df.iloc[idx, 4])
    yt = clean_val(df.iloc[idx, 5])
    d = clean_val(df.iloc[idx, 6])
    amz = clean_val(df.iloc[idx, 8])
    spt = clean_val(df.iloc[idx, 11])
    apl = clean_val(df.iloc[idx, 12])
    
    # Simple DSPI relative to fixed baselines
    def get_dspi(val, base):
        return round(val/base, 2) if val and base else 0

    print(f"{country:12} | {get_dspi(n, 17.99):.2f} | {get_dspi(yt, 13.99):.2f} | {get_dspi(d, 9.99):.2f} | {get_dspi(amz, 14.99):.2f} | {get_dspi(spt, 10.99):.2f} | {get_dspi(apl, 10.99):.2f}")
