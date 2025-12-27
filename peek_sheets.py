
import gspread
import pandas as pd
import os

SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"

def peek_sheets():
    cred_path = "google_sheets_mcp/credentials.json"
    gc = gspread.service_account(filename=cred_path)
    sh = gc.open_by_key(SHEET_ID)
    
    for name in ["Sheet1", "Sheet2"]:
        try:
            ws = sh.worksheet(name)
            print(f"\n--- Content of {name} (First 5 rows) ---")
            rows = ws.get_values()[:5]
            for r in rows:
                print(r)
        except Exception as e:
            print(f"Could not read {name}: {e}")

if __name__ == "__main__":
    peek_sheets()
