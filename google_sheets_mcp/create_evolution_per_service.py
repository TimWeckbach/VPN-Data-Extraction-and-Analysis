import gspread
import pandas as pd
import sys
import time
import numpy as np
import os
from google.oauth2.credentials import Credentials

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    print("--- Generating Service Evolution Charts (Excluding 'General Terms') ---")
    
    # Authenticate
    # Authenticate
    TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
    
    try:
        if not os.path.exists(TOKEN_FILE):
             print(f"Token file not found: {TOKEN_FILE}")
             return
             
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        gc = gspread.authorize(creds)
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit")
    except Exception as e:
        print(f"Auth/Connection Failed: {e}")
        return

    # 1. READ DATA
    csv_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # 2. PREPROCESS
    # Use New_Category
    if 'New_Category' in df.columns:
        df['Label'] = df['New_Category'].fillna(df['Label'])
    
    # Filter:
    # - Exclude "General Terms"
    # - Exclude Empty/Errors
    # - Valid Years (2016+)
    
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    df = df[
        (df['Label'] != "General Terms") & 
        (df['Label'] != "") & 
        (~df['Label'].str.contains("Error", na=False)) &
        (df['Label'].notna()) &
        (df['Year'] >= 2016) & (df['Year'] <= 2025)
    ]
    
    # Get List of Companies (Sorted by data volume magnitude to prioritize interesting ones)
    company_counts = df['Company'].value_counts()
    companies = company_counts.index.tolist()
    
    print(f"Found {len(companies)} companies with relevant data (excluding General Terms).")

    # 3. PREPARE SHEET
    sheet_name = "Service_Evolution"
    try:
        ws = sh.worksheet(sheet_name)
        sh.del_worksheet(ws)
        print("Deleted old sheet.")
    except gspread.WorksheetNotFound:
        pass
    
    rows_needed = len(companies) * 50 + 100 # Rough estimate
    ws = sh.add_worksheet(title=sheet_name, rows=rows_needed, cols=20)
    sheet_id = ws.id
    
    # 4. GENERATE CHARTS
    current_row = 1
    requests = []
    
    for company in companies:
        print(f"Processing {company}...")
        
        # Filter for company
        sub_df = df[df['Company'] == company]
        
        # Pivot: Index=Year, Cols=Label, Values=Count
        pivot = pd.crosstab(sub_df['Year'], sub_df['Label'])
        
        # Normalize to Percentage (Row-wise)
        # div(axis=0) divides by row sum. * 100 for percentage.
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
        pivot_pct = pivot_pct.fillna(0).round(1)
        
        # Reset index to make Year a column
        pivot_pct.reset_index(inplace=True)
        
        # Data Prepare
        headers = pivot_pct.columns.tolist() # ['Year', 'Account Action', ...]
        values = pivot_pct.values.tolist()
        
        # Write Title
        title = f"{company}: Evolution of Restriction Types (Relative %)"
        ws.update(range_name=f'A{current_row}', values=[[title]])
        current_row += 2
        
        # Write Data Table
        start_data_row = current_row
        ws.update(range_name=f'A{current_row}', values=[headers] + values)
        
        # Define ranges for Chart
        num_rows = len(values)
        num_cols = len(headers)
        
        # Header Row Index (0-based API)
        header_idx = current_row - 1
        
        # Series (Columns 1 to N)
        series_list = []
        for i in range(1, num_cols):
            series_list.append({
                "series": {
                    "sourceRange": {
                        "sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + num_rows + 1, "startColumnIndex": i, "endColumnIndex": i+1}]
                    }
                },
                "targetAxis": "LEFT_AXIS"
            })
            
        # Domain (Year - Col 0)
        domain = {
            "domain": {
                "sourceRange": {
                    "sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + num_rows + 1, "startColumnIndex": 0, "endColumnIndex": 1}]
                }
            }
        }
        
        # Add Chart Request
        requests.append({
            "addChart": {
                "chart": {
                    "spec": {
                        "title": title,
                        "basicChart": {
                            "chartType": "COLUMN", # Stacked Column is best for discrete years
                            "headerCount": 1,
                            "stackedType": "PERCENT_STACKED", # 100% Stacked
                            "legendPosition": "RIGHT_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Year"},
                                {"position": "LEFT_AXIS", "title": "Share of Specific Restrictions (%)"}
                            ],
                            "domains": [domain],
                            "series": series_list
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": sheet_id, "rowIndex": header_idx, "columnIndex": num_cols + 1},
                            "widthPixels": 600,
                            "heightPixels": 350
                        }
                    }
                }
            }
        })
        
        # Move cursor down for next company
        # Table height (num_rows + 1 header) + Chart height (approx 20 rows) + Padding
        current_row += len(values) + 25 
        
    # Execute batch update
    if requests:
        try:
            sh.batch_update({"requests": requests})
            print("Successfully created Service Evolution charts.")
        except Exception as e:
            print(f"Error creating charts: {e}")
    else:
        print("No charts generated (not enough data?).")

if __name__ == "__main__":
    main()
