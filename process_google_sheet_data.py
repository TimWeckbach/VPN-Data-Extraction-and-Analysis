
import pandas as pd
import re
import os

INPUT_FILE = r"Quantitative DATA\sheet1_raw.csv"
OUTPUT_FILE = r"Quantitative DATA\dspi_raw_data.csv"

# Exchange Rates (Dec 2024 / Jan 2025 Estimates)
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

def parse_price(price_str, country_name=None):
    if not isinstance(price_str, str) or not price_str.strip():
        return None, None
    s = price_str.strip().upper()
    
    # Heuristic Currency Detection
    found_curr = None
    
    # 1. Look for explicit code
    for curr in RATES_TO_USD.keys():
        if curr in s:
            found_curr = curr
            break
            
    # 2. Look for Symbols
    if not found_curr:
        if 'US$' in s: found_curr = 'USD'
        elif '$' in s:
             # Ambiguous '$':
             # If country is US -> USD
             # If country is Argentina/Canada/Australia -> keep generic, let fallback refine
             # Default fallback will be handled by caller or refined here if we trust country_name argument
             pass 
        elif '€' in s: found_curr = 'EUR'
        elif '£' in s: found_curr = 'GBP'
        elif ('₺' in s or 'TL' in s): found_curr = 'TRY'
        elif 'R$' in s: 
             if country_name and 'ARGENTINA' not in country_name.upper(): found_curr = 'BRL'
        elif '¥' in s: found_curr = 'JPY'
        elif 'CHF' in s: found_curr = 'CHF'
        elif '₹' in s: found_curr = 'INR'
        elif '₱' in s: found_curr = 'PHP'
        elif '₴' in s: found_curr = 'UAH'
        elif ' zł' in s: found_curr = 'PLN'

    # 3. Clean Number
    num_s = re.sub(r'[^\d,.]', '', s)
    if not num_s: return None, found_curr
    
    try:
        val = 0.0
        # European format handling
        if ',' in num_s and '.' in num_s:
            if num_s.rfind(',') > num_s.rfind('.'): # 1.234,56
                num_s = num_s.replace('.', '').replace(',', '.')
            else: # 1,234.56
                num_s = num_s.replace(',', '')
        elif ',' in num_s:
            if len(num_s.split(',')[-1]) == 2: num_s = num_s.replace(',', '.')
            else: num_s = num_s.replace(',', '')
            
        val = float(num_s)
        
        # Post-Parse Refinement for '$'
        if not found_curr and '$' in s:
             if country_name:
                 cn = country_name.upper()
                 if 'UNITED STATES' in cn or 'USA' in cn: found_curr = 'USD'
                 elif 'CANADA' in cn: found_curr = 'CAD'
                 elif 'AUSTRALIA' in cn: found_curr = 'AUD'
                 elif 'MEXICO' in cn: found_curr = 'MXN'
                 elif 'ARGENTINA' in cn: found_curr = None # Ambiguous (could be USD or ARS in data)
                 elif 'CHILE' in cn: found_curr = 'CLP'
                 elif 'COLOMBIA' in cn: found_curr = 'COP'
                 else: found_curr = 'USD' # Default for others (e.g. VPN prices in Turkey often in USD)
             else:
                 found_curr = 'USD'

        return val, found_curr
        
    except:
        return None, found_curr

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
        'Adobe Creative Cloud': 11,
        'Xbox Game Pass': 12,
        'NordVPN': 13,
        'ExpressVPN': 14
    }
    
    country_curr_map = {
        'United States': 'USD', 'USA': 'USD',
        'Germany': 'EUR', 'France': 'EUR', 'Spain': 'EUR', 'Italy': 'EUR', 'Netherlands': 'EUR',
        'United Kingdom': 'GBP', 'UK': 'GBP',
        'Turkey': 'TRY', 'turkiye': 'TRY',
        'Switzerland': 'CHF',
        'Japan': 'JPY',
        'Brazil': 'BRL',
        'India': 'INR',
        'Argentina': 'ARS',
        'Canada': 'CAD',
        'Australia': 'AUD',
        'Mexico': 'MXN',
        'Poland': 'PLN',
        'Ukraine': 'UAH'
        # Add more if needed, but the rates list covers most
    }

    # Load Referenced Salary Data
    salary_csv = r"Quantitative DATA\salary_data_external.csv"
    salary_lookup = {}
    if os.path.exists(salary_csv):
        sal_df = pd.read_csv(salary_csv)
        for _, srow in sal_df.iterrows():
            scurr = srow['Currency']
            sval = srow['Monthly_Wage_Local']
            srate = RATES_TO_USD.get(scurr, 1.0)
            if scurr == 'USD': srate=1.0 
            
            susd = sval * srate
            salary_lookup[srow['Country']] = susd
            if srow['Country'] == 'United States': salary_lookup['USA'] = susd
            if srow['Country'] == 'United Kingdom': salary_lookup['UK'] = susd

    results = []
    
    for idx, row in df.iterrows():
        country = str(row[0])
        if not country or country == 'nan' or 'Price of' in country: continue
        
        # SKIP generated rows
        if "USD Equivalent" in country or "↳" in country:
            continue

        # Clean Country Name
        country_clean = country.split('(')[0].split('[')[0].strip()
        
        # Use Referenced Salary
        salary_usd = salary_lookup.get(country_clean)
        # Try lowercase fallback
        if not salary_usd:
             for k,v in salary_lookup.items():
                 if k.lower() == country_clean.lower():
                     salary_usd = v
                     break

        for service, col_idx in services.items():
            if col_idx >= len(row): continue
            
            price_raw = str(row[col_idx])
            val, curr = parse_price(price_raw, country_clean)
            
            if val is not None:
                if not curr:
                    # Fallback Logic
                    if service in ['NordVPN', 'ExpressVPN']:
                        # VPNs often charge USD/EUR/Global regardless of user location
                        # If no symbol, assume USD for consistency in "Global" pricing
                        curr = 'USD'
                    else:
                        # For local services (Netflix, Spotify), default to Local Currency
                        curr = country_curr_map.get(country_clean, 'USD')
                
                # Special Case: 'Argentina' + '$' symbol -> Assume ARS unless explicit
                # Logic handled in parse_price returns None for Argentina '$' so fallback hits here.
                # If fallback hits here for Argentina:
                if curr is None and 'Argentina' in country_clean:
                     curr = 'ARS'
                
                # Check rate
                rate = RATES_TO_USD.get(curr, 1.0)
                price_usd = val * rate
                
                results.append({
                    'Year': 2024,
                    'Service': service,
                    'Country': country_clean,
                    'Original_Price': val,
                    'Currency': curr,
                    'Price_USD': round(price_usd, 2),
                    'Monthly_Salary_USD': round(salary_usd, 2) if salary_usd else None
                })
                
    # Create DF
    final_df = pd.DataFrame(results)
    
    # Calculate DSPI (Baseline = USA Price)
    us_prices = {}
    us_rows = final_df[final_df['Country'].isin(['United States', 'USA'])]
    if not us_rows.empty:
        us_prices = us_rows.set_index('Service')['Price_USD'].to_dict()
        
    import datetime
    conversion_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_metrics(row):
        base = us_prices.get(row['Service'])
        dspi = None
        diff = None
        
        if base and base > 0:
            dspi = round(row['Price_USD'] / base, 2)
            diff = round(row['Price_USD'] - base, 2)
            
        return pd.Series([dspi, diff])
        
    final_df[['DSPI', 'Real_Diff_USD']] = final_df.apply(get_metrics, axis=1)
    
    # User requested "Replace PPP with... Median Wage". 
    # We rename the column to be explicit: 'Affordability_Wage_Based'
    # Calculation: % of Monthly Wage.
    final_df['Affordability_Wage_Based_%'] = final_df.apply(
        lambda x: (x['Price_USD'] / x['Monthly_Salary_USD'] * 100) if x['Monthly_Salary_USD'] else None, 
        axis=1
    )
    
    # Metadata
    final_df['Conversion_Date'] = conversion_timestamp
    final_df['Conversion_Source'] = "Manual Estimates (Dec 2024/Jan 2025)"

    print(f"Extracted {len(final_df)} valid price points.")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_sheet()
