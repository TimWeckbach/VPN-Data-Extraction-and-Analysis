import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import gspread

# Paths
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email']

def main():
    print("--- DIAGNOSTIC START ---")
    
    # 1. Check Token File
    if not os.path.exists(TOKEN_FILE):
        print(f"FAIL: Token file not found at {TOKEN_FILE}")
        return
    print("PASS: Token file exists.")

    # 2. Load Credentials
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        print(f"PASS: Credentials loaded.")
        print(f"Token valid: {creds.valid}")
        print(f"Token expired: {creds.expired}")
    except Exception as e:
        print(f"FAIL: Could not load credentials: {e}")
        return

    # 3. Check User Identity
    try:
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        email = user_info.get('email')
        print(f"AUTHENTICATED AS: {email}")
    except Exception as e:
        print(f"WARNING: Could not fetch user info (might be scope issue): {e}")

    # 4. Try GSpread Access
    try:
        gc = gspread.authorize(creds)
        print("PASS: GSpread authorized.")
        
        # TEST CREATE
        print("Attempting to CREATE a new sheet...")
        new_sh = gc.create("Agent Connectivity Test")
        print(f"SUCCESS! Created new sheet: {new_sh.url}")
        print("Attempting to share this new sheet with you (if I knew your email)...")
        # cleanup
        # gc.del_spreadsheet(new_sh.id) 
        
        print(f"Now Attempting to open TARGET Sheet ID: {SHEET_ID}")
        sh = gc.open_by_key(SHEET_ID)
        print(f"SUCCESS! Opened Target Sheet: '{sh.title}'")
    except Exception as e:
        print(f"FAIL: GSpread Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
