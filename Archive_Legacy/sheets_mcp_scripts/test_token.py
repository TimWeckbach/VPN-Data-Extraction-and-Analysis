from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import gspread

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
token_file = 'token_default.json'

try:
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token refreshed successfully.")
        else:
            print("Token is invalid and cannot be refreshed.")
            exit(1)
    
    gc = gspread.authorize(creds)
    # Try to list sheets just to verify access
    # We will use the URL provided by the user previously
    url = "https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit?gid=804760606#gid=804760606"
    sh = gc.open_by_url(url)
    print(f"Successfully accessed sheet: {sh.title}")
    
except Exception as e:
    print(f"Error: {e}")
