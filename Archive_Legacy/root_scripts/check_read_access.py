import gspread
from google.oauth2.credentials import Credentials
import os

TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    if not os.path.exists(TOKEN_FILE):
        print("No token file found.")
        return

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        gc = gspread.authorize(creds)
        
        print(f"Attempting to open Sheet: {SHEET_ID}")
        sh = gc.open_by_key(SHEET_ID)
        print(f"SUCCESS: Read Access Confirmed.")
        print(f"Title: {sh.title}")
        print(f"Worksheets: {[ws.title for ws in sh.worksheets()]}")
        
    except Exception as e:
        print(f"FAILURE: No Read Access. Error: {e}")

if __name__ == "__main__":
    main()
