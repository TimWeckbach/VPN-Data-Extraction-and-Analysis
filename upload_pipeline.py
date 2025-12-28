import gspread
import pandas as pd
import os
from google.oauth2.credentials import Credentials

# Configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit"
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

FILES_TO_UPLOAD = {
    "DSPI_Data": r"Quantitative DATA\Sheets_Import_DSPI.csv",
    "Qual_Counts": r"Quantitative DATA\Sheets_Import_Qual_Counts.csv",
    "Qual_Timeline": r"Quantitative DATA\Sheets_Import_Qual_Timeline.csv",
    "Correlation_Data": r"Quantitative DATA\Sheets_Import_Correlation.csv"
}

def main():
    print("--- STARTING UPLOAD PIPELINE ---")
    
    # 1. Authenticate
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: Token file not found at {TOKEN_FILE}")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    gc = gspread.authorize(creds)
    
    # 2. Open Sheet
    print(f"Opening Sheet: {SHEET_URL}")
    try:
        sh = gc.open_by_url(SHEET_URL)
    except Exception as e:
        print(f"Error opening sheet: {e}")
        return

    # 3. Upload Files
    for tab_name, file_path in FILES_TO_UPLOAD.items():
        if not os.path.exists(file_path):
            print(f"Skipping {tab_name}: File not found ({file_path})")
            continue
            
        print(f"Uploading '{file_path}' to tab '{tab_name}'...")
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            df = df.fillna("")
            data = [df.columns.values.tolist()] + df.values.tolist()
            
            # Get or Create Worksheet
            try:
                ws = sh.worksheet(tab_name)
                ws.clear()
            except gspread.WorksheetNotFound:
                ws = sh.add_worksheet(title=tab_name, rows=len(data)+20, cols=len(data[0])+5)
            
            # Update Data
            ws.update(range_name='A1', values=data)
            print(f" - Success! ({len(data)} rows)")
            
        except Exception as e:
            print(f" - FAILED: {e}")

    print("\n--- UPLOAD COMPLETE ---")
    print(f"View your data here: {SHEET_URL}")

if __name__ == "__main__":
    main()
