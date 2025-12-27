
import gspread
import pandas as pd
import os

# ID from previous grep
SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"

def list_tabs():
    cred_path = "credentials.json"
    if not os.path.exists(cred_path):
        cred_path = "google_sheets_mcp/credentials.json"
    
    if not os.path.exists(cred_path):
        print("Error: credentials.json not found in root or google_sheets_mcp/")
        return

    print(f"Connecting using {cred_path}...")
    try:
        gc = gspread.service_account(filename=cred_path)
        sh = gc.open_by_key(SHEET_ID)
        
        print("\n--- Available Worksheets ---")
        for ws in sh.worksheets():
            print(f"- {ws.title}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    list_tabs()
