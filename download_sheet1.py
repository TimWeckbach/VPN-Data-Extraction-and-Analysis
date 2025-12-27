
import gspread
import pandas as pd
import os

SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"

def download_sheet1():
    cred_path = "google_sheets_mcp/credentials.json"
    gc = gspread.service_account(filename=cred_path)
    sh = gc.open_by_key(SHEET_ID)
    
    ws = sh.worksheet("Sheet1")
    data = ws.get_all_values()
    
    df = pd.DataFrame(data)
    # Save raw first
    df.to_csv(r"Quantitative DATA\sheet1_raw.csv", index=False, header=False)
    print("Downloaded Sheet1 to Quantitative DATA\sheet1_raw.csv")

if __name__ == "__main__":
    download_sheet1()
