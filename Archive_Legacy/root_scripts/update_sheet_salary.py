
import gspread
import pandas as pd
import os
import re

SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"
SALARY_CSV = r"Quantitative DATA\salary_data_external.csv"
CRED_PATH = "google_sheets_mcp/credentials.json"

# Rates from previous step
RATES_TO_USD = {
    'EUR': 1.09, 'USD': 1.0, 'GBP': 1.27, 'CHF': 1.13,
    'TRY': 0.032, 'ARS': 0.0012, 'INR': 0.012, 'BRL': 0.20,
    'JPY': 0.0067
}

def update_salary_columns():
    if not os.path.exists(SALARY_CSV):
        print("External salary data not found.")
        return

    # 1. Load External Data
    ext_df = pd.read_csv(SALARY_CSV)
    # Create lookup dict: Country -> {USD_Val, Source}
    lookup = {}
    for _, row in ext_df.iterrows():
        country = row['Country']
        local_val = row['Monthly_Wage_Local']
        curr = row['Currency']
        src = row['Source']
        
        rate = RATES_TO_USD.get(curr, 1.0)
        usd_val = local_val * rate
        
        lookup[country.lower()] = {
            'usd': round(usd_val, 2),
            'source': src
        }

    # 2. Connect to Sheet
    print("Connecting to Google Sheet...")
    gc = gspread.service_account(filename=CRED_PATH)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet("Sheet1")
    
    # 3. Read existing data (Column A is Country)
    # Get all values to map row indices
    rows = ws.get_all_values()
    
    # Prepare updates
    # We will update Col B (Index 1) with Source, and Col C (Index 2) with Salary USD
    # Header row is 0
    
    updates = []
    
    # Set Headers
    # B1 -> "Data Source"
    # C1 -> "Avg Monthly Salary (USD)"
    updates.append({'range': 'B1', 'values': [['Data Source']]})
    updates.append({'range': 'C1', 'values': [['Avg Monthly Salary (USD)']]})
    
    print(f"Scanning {len(rows)} rows...")
    
    batch_data = [] # List of cells to update? gspread batch_update is complex.
    # Simpler: ws.update('B2:C100', [[...], [...]])
    
    # Let's construct the entire B and C column data list matching the rows
    col_b_data = []
    col_c_data = []
    
    for i in range(1, len(rows)): # Skip header
        row_data = rows[i]
        if not row_data: 
            col_b_data.append([""])
            col_c_data.append([""])
            continue
            
        country_raw = row_data[0]
        # Clean country name: "Turkey (Turkiye)" -> "turkey"
        c_clean = country_raw.split('(')[0].strip().lower()
        
        if c_clean in lookup:
            data = lookup[c_clean]
            col_b_data.append([data['source']])     # Source in B
            col_c_data.append([data['usd']])        # Salary in C
        else:
            # If not in our verified list, we leave empty or keep existing?
            # User said "delete / replace all the made up data". 
            # Implies we should clear non-verified data?
            # I will clear them to be safe and strictly scientific.
            col_b_data.append([""])
            col_c_data.append([""])
            
    # Batch Update
    # Range starts from Row 2
    range_b = f"B2:B{len(rows)}"
    range_c = f"C2:C{len(rows)}"
    
    print("Updating Sheet...")
    ws.update(range_name=range_b, values=col_b_data)
    ws.update(range_name=range_c, values=col_c_data)
    
    print("Success: Updated Google Sheet with verified salary data.")

if __name__ == "__main__":
    update_salary_columns()
