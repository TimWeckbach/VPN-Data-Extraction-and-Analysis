
import gspread
import pandas as pd
import os
import re
from copy import deepcopy

# --- Configuration ---
SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"
CRED_PATH = "google_sheets_mcp/credentials.json"

# --- Exchange Rates (Dec 2024 / Jan 2025 Estimates) ---
RATES_TO_USD = {
    'EUR': 1.09, 'USD': 1.0, 'GBP': 1.27, 'CHF': 1.13,
    'TRY': 0.032, 'ARS': 0.0012, 'INR': 0.012, 'BRL': 0.20,
    'JPY': 0.0067, 'CAD': 0.74, 'AUD': 0.66, 'MXN': 0.059,
    'PLN': 0.25, 'ZAR': 0.053, 'COP': 0.00026, 'EGP': 0.021,
    'IDR': 0.000064, 'VND': 0.000041, 'PHP': 0.018, 'THB': 0.028,
    'MYR': 0.21, 'SGD': 0.74, 'HKD': 0.13, 'KRW': 0.00075,
    'CLP': 0.0011, 'PEN': 0.27, 'NGN': 0.0007, 'PKR': 0.0036,
    'UAH': 0.026, 'HUF': 0.0028, 'CZK': 0.043, 'DKK': 0.15, 
    'NOK': 0.096, 'SEK': 0.096, 'ILS': 0.27, 'SAR': 0.27, 
    'AED': 0.27, 'RON': 0.22, 'BGN': 0.55
}

# --- Parsing Logic --
def parse_price(price_str, country_name):
    if not isinstance(price_str, str) or not price_str.strip():
        return None, None
    s = price_str.strip().upper()
    
    # Heuristic Currency Detection
    found_curr = None
    rate = 1.0
    
    # 1. Look for explicit code
    for curr in RATES_TO_USD.keys():
        if curr in s:
            found_curr = curr
            break
            
    # 2. Look for Symbols
    if not found_curr:
        if '€' in s: found_curr = 'EUR'
        elif '£' in s: found_curr = 'GBP'
        elif ('₺' in s or 'TL' in s): found_curr = 'TRY'
        elif 'R$' in s: 
             if 'Argentina' not in country_name: found_curr = 'BRL'
        elif '¥' in s: found_curr = 'JPY'
        elif 'CHF' in s: found_curr = 'CHF'
        elif '₹' in s: found_curr = 'INR'
        elif '₱' in s: found_curr = 'PHP'
        elif '₴' in s: found_curr = 'UAH'
        elif ' zł' in s: found_curr = 'PLN'

    # 3. Fallback: Identify by Country Name if still unknown
    if not found_curr:
        c_map = {
            'Turkey': 'TRY', 'Turkiye': 'TRY',
            'Argentina': 'ARS',
            'India': 'INR',
            'Brazil': 'BRL',
            'United Kingdom': 'GBP', 'UK': 'GBP',
            'Germany': 'EUR', 'France': 'EUR', 'Italy': 'EUR', 'Spain': 'EUR',
            'Switzerland': 'CHF',
            'Japan': 'JPY',
            'Poland': 'PLN',
            'Ukraine': 'UAH',
            'Philippines': 'PHP',
            'Egypt': 'EGP',
            'Nigeria': 'NGN',
            'Pakistan': 'PKR',
            'South Africa': 'ZAR'
        }
        for k, v in c_map.items():
            if k in country_name:
                found_curr = v
                break

    # 4. Clean Number
    num_s = re.sub(r'[^\d,.]', '', s)
    if not num_s: return None, found_curr
    
    try:
        val = 0.0
        # European format handling (1.000,00 vs 1,000.00)
        # Heuristic: if comma appears after dot, or comma is last separator
        if ',' in num_s and '.' in num_s:
            if num_s.rfind(',') > num_s.rfind('.'): # 1.234,56
                num_s = num_s.replace('.', '').replace(',', '.')
            else: # 1,234.56
                num_s = num_s.replace(',', '')
        elif ',' in num_s:
            # If comma is decimal separator (e.g. 12,99) 
            if len(num_s.split(',')[-1]) == 2: num_s = num_s.replace(',', '.')
            else: num_s = num_s.replace(',', '')
            
        val = float(num_s)
        return val, found_curr
    except:
        return None, found_curr

def process_sheet():
    print(f"Connecting to Google Sheet {SHEET_ID}...")
    if not os.path.exists(CRED_PATH):
        print("Error: Credentials not found.")
        return

    gc = gspread.service_account(filename=CRED_PATH)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet("Sheet1")
    
    rows = ws.get_all_values()
    if not rows:
        print("Sheet is empty.")
        return

    header = rows[0]
    new_rows = [header]
    
    # Columns Indices (0-based)
    # 0: Country, 1: Source, 2: Salary, 3: (Unknown), 4+: Services
    SERVICE_START_IDX = 4
    
    print(f"Processing {len(rows)-1} rows...")
    
    for i in range(1, len(rows)):
        row = rows[i]
        country_cell = row[0]
        
        # SKIP if this is already a generated row (starts with indent or "USD")
        if "USD Equivalent" in country_cell or "   ↳" in country_cell:
            continue
            
        # Clean current country name (remove old rates if re-running)
        # e.g. "Turkey (Rate: 1 TRY...)" -> "Turkey"
        country_clean = country_cell.split(' (Rate:')[0].strip()
        country_clean = country_clean.split(' [Rate:')[0].strip()
        
        # Parse logic
        detected_curr = None
        detected_vals = {} # idx -> val
        
        # Scan service columns to identify currency
        for col_idx in range(SERVICE_START_IDX, len(row)):
            val_str = row[col_idx]
            val, curr = parse_price(val_str, country_clean)
            if val is not None:
                detected_vals[col_idx] = val
            if curr and not detected_curr:
                detected_curr = curr
                
        # Default to USD if United States
        if 'United States' in country_clean or 'USA' in country_clean:
            detected_curr = 'USD'

        # If we have a currency and it's NOT USD, generate conversion row
        if detected_curr and detected_curr != 'USD':
            rate = RATES_TO_USD.get(detected_curr, 0.0)
            
            if rate > 0:
                # 1. Update Original Row country name
                new_country_name = f"{country_clean} [Rate: 1 {detected_curr} = {rate} USD]"
                modified_row = list(row)
                modified_row[0] = new_country_name
                new_rows.append(modified_row)
                
                # 2. Create USD Row
                usd_row = [""] * len(row)
                usd_row[0] = "   ↳ USD Equivalent" # Indented
                
                # Convert values
                for col_idx, val in detected_vals.items():
                    usd_val = val * rate
                    usd_row[col_idx] = f"${usd_val:.2f}"
                
                new_rows.append(usd_row)
            else:
                # Rate unknown, just keep original
                new_rows.append(row)
        else:
            # Already USD or unknown, just keep
            # Clean name just in case
            modified_row = list(row)
            modified_row[0] = country_clean
            new_rows.append(modified_row)
            
    # Write back
    print(f"Writing {len(new_rows)} rows (original + conversions)...")
    ws.clear()
    ws.update('A1', new_rows)
    print("Done!")

if __name__ == "__main__":
    process_sheet()
