import pandas as pd
import re
import datetime
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
        if 'HK$' in s: found_curr = 'HKD'
        elif 'US$' in s: found_curr = 'USD'
        elif '$' in s:
             # Ambiguous '$':
             # If country is US -> USD
             # If country is Argentina/Canada/Australia -> keep generic, let fallback refine
             # Default fallback will be handled by caller or refined here if we trust country_name argument
             pass 
        elif '€' in s: found_curr = 'EUR'
        elif '£' in s: found_curr = 'GBP'
        elif ('₺' in s or 'TL' in s): found_curr = 'TRY'
        elif 'R$' in s: found_curr = 'BRL'
        elif '¥' in s: found_curr = 'JPY'
        elif 'CHF' in s: found_curr = 'CHF'
        elif '₹' in s: found_curr = 'INR'
        elif '₱' in s: found_curr = 'PHP'
        elif '₴' in s: found_curr = 'UAH'
        elif ' zł' in s: found_curr = 'PLN'
        elif '฿' in s: found_curr = 'THB'

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
        
        # SKIP if country name became empty (e.g. metadata rows starting with '[')
        if not country_clean:
            continue
        
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
                if curr is None and 'Argentina' in country_clean:
                     curr = 'ARS'

                # Special Case: 'Pakistan'
                # Raw data has 'Rs' or 'Rs.' which might be missed, or '₹' (INR symbol used for Rupee).
                # Microsoft: "Rs22,999.00", Adobe: "Rs 18,899"
                if 'Pakistan' in country_clean:
                    # Specific Exception: Adobe and VPNs can be USD. 
                    # Everything else (Microsoft, Netflix, etc.) must be PKR.
                    if service not in ['NordVPN', 'ExpressVPN', 'Adobe Creative Cloud']:
                         if curr == 'USD' or curr == 'INR' or curr is None:
                             curr = 'PKR'

                # Special Case: 'Brazil'
                # Netlfix/Spotify etc are BRL. NordVPN is BRL too. ExpressVPN likely USD.
                if 'Brazil' in country_clean:
                    if service not in ['ExpressVPN']:
                        if curr == 'USD' or curr is None:
                            curr = 'BRL'

                # Special Case: 'Argentina'
                # NordVPN is priced in BRL for Argentina/Brazil according to the VPN Rule.
                if 'Argentina' in country_clean:
                     if service == 'NordVPN':
                          curr = 'BRL'
                
                # Check rate
                rate = RATES_TO_USD.get(curr, 1.0)
                price_usd_static = val * rate
                
                results.append({
                    'Year': 2024,
                    'Service': service,
                    'Country': country_clean,
                    'Original_Price': val,               # Col D
                    'Currency': curr,                    # Col E
                    'Exchange_Rate': rate,               # Col F
                    'Price_USD_Static': price_usd_static, # Helper for US baseline
                    'Monthly_Salary_USD': round(salary_usd, 2) if salary_usd else "" # Col J (Target)
                })
                
    # Create DF
    final_df = pd.DataFrame(results)
    
    # Calculate US Baselines (Using the static calculation)
    # We need a fallback if US price missing.
    us_prices = {}
    us_rows = final_df[final_df['Country'].isin(['United States', 'USA'])]
    if not us_rows.empty:
        us_prices = us_rows.set_index('Service')['Price_USD_Static'].to_dict()
        
    def get_us_baseline(service):
        return us_prices.get(service, "")
        
    final_df['US_Baseline_Price'] = final_df['Service'].apply(get_us_baseline) # Col H

    # NOW CONSTRUCT THE EXPORT DF WITH FORMULAS
    # Fixed Column Layout for Formulas:
    # A: Year
    # B: Service
    # C: Country
    # D: Original_Price
    # E: Currency
    # F: Exchange_Rate
    # G: Price_USD (Formula: =D*F)
    # H: US_Baseline_Price
    # I: DSPI (Formula: =G/H)
    # J: Monthly_Salary_USD
    # K: Affordability_% (Formula: =G/J)
    # L: Real_Diff_USD (Formula: =G-H)
    # M: Real_Diff_USD_% (Formula: =L/H)

    export_rows = []
    
    # Header Row is 1. Data starts at 2.
    for i, row in final_df.iterrows():
        row_num = i + 2
        
        # Formulas
        f_price_usd = f"=D{row_num}*F{row_num}"
        
        # Safe Division for DSPI
        if row['US_Baseline_Price']:
             f_dspi = f"=G{row_num}/H{row_num}"
             f_real_diff = f"=G{row_num}-H{row_num}"
             f_real_diff_pct = f"=L{row_num}/H{row_num}"
        else:
             f_dspi = ""
             f_real_diff = ""
             f_real_diff_pct = ""
             
        # Safe Division for Affordability
        if row['Monthly_Salary_USD']:
             f_afford = f"=G{row_num}/J{row_num}"
        else:
             f_afford = ""

        export_rows.append({
            'Year': row['Year'],
            'Service': row['Service'],
            'Country': row['Country'],
            'Original_Price': row['Original_Price'],
            'Currency': row['Currency'],
            'Exchange_Rate': row['Exchange_Rate'],
            'Price_USD': f_price_usd,
            'Price_USD_Static': row['Price_USD_Static'],
            'US_Baseline_Price': row['US_Baseline_Price'],
            'DSPI': f_dspi,
            'Monthly_Salary_USD': row['Monthly_Salary_USD'],
            'Affordability_Wage_Based_%': f_afford,
            'Real_Diff_USD': f_real_diff,
            'Real_Diff_USD_%': f_real_diff_pct,
            'Conversion_Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    export_df = pd.DataFrame(export_rows)
    print(f"Extracted {len(export_df)} valid price points.")
    
    # Add Date Column
    export_df['Date Collected'] = "December 2025"

    # Save to CSV
    # Note: When saving to CSV, formulas like "=A1+B1" are just text strings. 
    # The 'USER_ENTERED' option in upload_pipeline.py will interpret them.
    export_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_sheet()
