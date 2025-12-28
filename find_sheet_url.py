from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build('drive', 'v3', credentials=creds)
    
    # List recent spreadsheets to see what exists
    print("Listing recent spreadsheets...")
    query_all = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    results = service.files().list(q=query_all, pageSize=5, orderBy="modifiedTime desc", fields="files(id, name, webViewLink)").execute()
    existing_files = results.get('files', [])
    for f in existing_files:
        print(f" - Found: '{f['name']}' (ID: {f['id']})")
        if f['name'] == 'Price_Analysis_RQ1':
            print(f"MATCH FOUND: URL='{f['webViewLink']}'")
            return

    # If not found, create it
    print("\nTarget 'Price_Analysis_RQ1' not found. Creating it...")
    file_metadata = {
        'name': 'Price_Analysis_RQ1',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    file = service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    print(f"CREATED NEW SHEET: ID='{file.get('id')}', URL='{file.get('webViewLink')}'")

if __name__ == '__main__':
    main()
