
import pandas as pd
import re
import os

INPUT_FILE = r"Quantitative DATA\sheet1_raw.csv"
OUTPUT_FILE = r"Quantitative DATA\dspi_raw_data.csv"

# Exchange Rates (Approximate 2024 for conversion)
# We need to detect currency from string if possible, or assume based on country.
# This is hard. 
# Plan B: The user wants "Real Data". 
# IF the sheet has a "USD" column I missed, that would be great.
# Looking at the raw csv again...
# Turkey: "289.99 TRY" -> Need to parse 289.99 and know it is TRY.

RATES_TO_USD = {
    'EUR': 1.09, 'USD': 1.0, 'GBP': 1.27, 'CHF': 1.13,
    'TRY': 0.032, 'ARS': 0.0012, 'INR': 0.012, 'BRL': 0.20,
    'JPY': 0.0067, 'CAD': 0.74, 'AUD': 0.66, 'MXN': 0.059,
    'PLN': 0.25, 'ZAR': 0.053, 'COP': 0.00026, 'EGP': 0.021,
    'IDR': 0.000064, 'VND': 0.000041, 'PHP': 0.018, 'THB': 0.028,
    'MYR': 0.21, 'SGD': 0.74, 'HKD': 0.13, 'KRW': 0.00075,
    'CLP': 0.0011, 'PEN': 0.27, 'NGN': 0.0007, 'PKR': 0.0036,
    'UAH': 0.026, 'PHP': 0.018, 'HUF': 0.0028, 'CZK': 0.043, 'DKK': 0.15, 'NOK': 0.096, 'SEK': 0.096,
    'ILS': 0.27, 'SAR': 0.27, 'AED': 0.27, 'RON': 0.22, 'BGN': 0.55
}

def parse_price(price_str, country=None):
    if not isinstance(price_str, str) or not price_str.strip():
        return None, None
    
    # Clean string
    s = price_str.strip().upper()
    
    # Detect Currency
    found_curr = None
    rate = 1.0
    
    # Prioritize Explicit Code
    for curr, r in RATES_TO_USD.items():
        if curr in s:
            found_curr = curr
            rate = r
            break
            
    # Common symbols fallback
    if not found_curr:
        if '€' in s: found_curr = 'EUR'; rate = RATES_TO_USD['EUR']
        elif '£' in s: found_curr = 'GBP'; rate = RATES_TO_USD['GBP']
        elif ('₺' in s or 'TL' in s) and (country != 'Argentina'): found_curr = 'TRY'; rate = RATES_TO_USD['TRY']
        elif 'R$' in s: 
             if country == 'Argentina': pass # Avoid BRL confusion
             else: found_curr = 'BRL'; rate = RATES_TO_USD['BRL']
        elif '¥' in s: found_curr = 'JPY'; rate = RATES_TO_USD['JPY']
        elif 'CHF' in s: found_curr = 'CHF'; rate = RATES_TO_USD['CHF']
        elif '₹' in s: found_curr = 'INR'; rate = RATES_TO_USD['INR']
        elif '₱' in s: found_curr = 'PHP'; rate = RATES_TO_USD['PHP']
        elif '₴' in s: found_curr = 'UAH'; rate = RATES_TO_USD['UAH']
        elif ' zł' in s: found_curr = 'PLN'; rate = RATES_TO_USD['PLN']
        elif 'kr' in s: 
             pass

    # Remove non-numeric chars (except dots and commas)
    num_s = re.sub(r'[^\d,.]', '', s)
    if not num_s: return None, None
    
    try:
        val = 0.0
        # European format handling
        if ',' in num_s and '.' in num_s:
            if num_s.find(',') > num_s.find('.'): # 1.234,56
                num_s = num_s.replace('.', '').replace(',', '.')
            else: # 1,234.56
                num_s = num_s.replace(',', '')
        elif ',' in num_s:
            # If comma is decimal separator (e.g. 12,99) 
            # Heuristic: if country is in Europe/South America usually comma is decimal.
            # But in code we need to be careful.
            if len(num_s.split(',')[1]) == 2: num_s = num_s.replace(',', '.')
            else: num_s = num_s.replace(',', '')
                
        val = float(num_s)
        return val, found_curr
        
    except:
        return None, None

def process_sheet():
    print("Processing Google Sheet data...")
    df = pd.read_csv(INPUT_FILE, header=0)
    
    # Map: 'Netflix' -> Col 4, etc.
    services = {
        'Netflix': 4,
        'Youtube Premium': 5,
        'Disney+': 6, 
        'Amazon Prime': 7,
        'Spotify': 8,
        'Apple Music': 9,
        'Microsoft 365': 10, 
        'Adobe Creative Cloud': 11, # Standardized Name
        'Xbox Game Pass': 12, # Standardized Name
        'NordVPN': 13,
        'ExpressVPN': 14
    }
    
    # Country-Currency Map for Fallbacks (unchanged - relying on imports usually)
    country_curr_map = {
        'United States': 'USD', 'USA': 'USD',
        'Germany': 'EUR', 'France': 'EUR', 'Spain': 'EUR', 'Italy': 'EUR', 'Netherlands': 'EUR', 'Monaco': 'EUR', 'Luxembourg': 'EUR', 'Ireland': 'EUR', 'Austria': 'EUR', 'Finland': 'EUR', 'Belgium': 'EUR', 'Portugal': 'EUR', 'Greece': 'EUR', 'Estonia': 'EUR', 'Latvia': 'EUR', 'Lithuania': 'EUR', 'Slovakia': 'EUR', 'Slovenia': 'EUR',
        'United Kingdom': 'GBP', 'UK': 'GBP',
        'Turkey': 'TRY', 'Turkiye': 'TRY',
        'Switzerland': 'CHF', 'Liechtenstein': 'CHF',
        'Japan': 'JPY',
        'Brazil': 'BRL',
        'India': 'INR',
        'Argentina': 'ARS',
        'Canada': 'CAD',
        'Australia': 'AUD',
        'Mexico': 'MXN',
        'Poland': 'PLN',
        'Ukraine': 'UAH',
        'Philippines': 'PHP',
        'Indonesia': 'IDR',
        'Vietnam': 'VND',
        'Thailand': 'THB',
        'Malaysia': 'MYR',
        'Singapore': 'SGD',
        'Hong Kong': 'HKD',
        'South Korea': 'KRW',
        'Chile': 'CLP',
        'Colombia': 'COP',
        'Peru': 'PEN',
        'South Africa': 'ZAR',
        'Nigeria': 'NGN',
        'Pakistan': 'PKR',
        'Egypt': 'EGP',
        'Saudi Arabia': 'SAR',
        'UAE': 'AED',
        'Israel': 'ILS',
        'Russia': 'RUB', # 0.011 if needed
        'Hungary': 'HUF',
        'Czech Republic': 'CZK',
        'Sweden': 'SEK',
        'Norway': 'NOK',
        'Denmark': 'DKK'
    }

    # Load Referenced Salary Data
    salary_csv = r"Quantitative DATA\salary_data_external.csv"
    salary_lookup = {}
    if os.path.exists(salary_csv):
        sal_df = pd.read_csv(salary_csv)
        for _, srow in sal_df.iterrows():
            # Convert to USD
            scurr = srow['Currency']
            sval = srow['Monthly_Wage_Local']
            srate = RATES_TO_USD.get(scurr, 1.0)
            # ... (rest is same)
            if scurr == 'USD': srate=1.0 # explicit
            
            susd = sval * srate
            salary_lookup[srow['Country']] = susd
            # Also map USA equivalents
            if srow['Country'] == 'United States': salary_lookup['USA'] = susd
            if srow['Country'] == 'United Kingdom': salary_lookup['UK'] = susd

    results = []
    
    for idx, row in df.iterrows():
        country = str(row[0])
        if not country or country == 'nan' or 'Price of' in country: continue
        
        # SKIP generated rows (visual aids)
        if "USD Equivalent" in country or "↳" in country:
            continue

        # Clean Country Name
        # Handle "Turkey (Turkiye)" and "Turkey [Rate: ...]"
        country_clean = country.split('(')[0].split('[')[0].strip()
        
        # Use Referenced Salary
        salary_usd = salary_lookup.get(country_clean)
        if not salary_usd and country_clean in salary_lookup:
             salary_usd = salary_lookup[country_clean]

        for service, col_idx in services.items():
            if col_idx >= len(row): continue
            
            price_raw = str(row[col_idx])
            val, curr = parse_price(price_raw, country_clean) # PASS COUNTRY
            
            if val is not None:
                if not curr:
                    curr = country_curr_map.get(country_clean, 'USD')
                
                rate = RATES_TO_USD.get(curr, 1.0)
                price_usd = val * rate
                
                results.append({
                    'Year': 2024,
                    'Service': service,
                    'Country': country_clean,
                    'Original_Price': val,
                    'Currency': curr,
                    'Price_USD': round(price_usd, 2),
                    'Monthly_Salary_USD': round(salary_usd, 2) if salary_usd else None,
                    'Salary_Source_Ref': 'OECD/TradingEconomics' if salary_usd else 'Missing' 
                })

    # Create DF
    final_df = pd.DataFrame(results)
    
    # Calculate DSPI (Baseline = USA Price)
    # Get US prices per Service
    us_prices = final_df[final_df['Country'] == 'United States'].set_index('Service')['Price_USD'].to_dict()
    if not us_prices:
        us_prices = final_df[final_df['Country'] == 'USA'].set_index('Service')['Price_USD'].to_dict()
        
    def get_dspi(row):
        base = us_prices.get(row['Service'])
        if base and base > 0:
            return round(row['Price_USD'] / base, 2)
        return None
        
    final_df['DSPI'] = final_df.apply(get_dspi, axis=1)
    
    # Calculate Affordability metric
    # Only if we have Referenced Salary Data
    final_df['Affordability_%'] = final_df.apply(lambda x: (x['Price_USD'] / x['Monthly_Salary_USD'] * 100) if x['Monthly_Salary_USD'] else None, axis=1)

    print(f"Extracted {len(final_df)} valid price points.")
    # Filter to only rows where we have BOTH price and trusted salary for the heatmap
    heatmap_ready_df = final_df.dropna(subset=['Affordability_%'])
    print(f"Heatmap ready rows (with trusted salary): {len(heatmap_ready_df)}")
    
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_sheet()
