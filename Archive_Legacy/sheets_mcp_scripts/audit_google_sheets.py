from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Define the scopes we need
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
token_file = 'token_personal.json'
spreadsheet_id = '1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk'

try:
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    # Get spreadsheet metadata including all sheets
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get('sheets', [])
    
    print(f"Auditing Spreadsheet: {spreadsheet.get('properties', {}).get('title')}")
    print(f"Total Tabs: {len(sheets)}")
    
    results = []
    for sheet in sheets:
        sheet_name = sheet['properties']['title']
        has_charts = 'charts' in sheet
        chart_count = len(sheet.get('charts', []))
        
        info = f"[Tab] {sheet_name}: {chart_count} charts"
        print(info)
        results.append(info)
        
        if has_charts:
            for i, chart in enumerate(sheet['charts']):
                title = chart.get('spec', {}).get('title', 'No Title')
                print(f"  - Chart {i+1}: {title}")
                results.append(f"  - Chart {i+1}: {title}")

    with open('google_sheets_audit_results.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

except Exception as e:
    print(f"Error: {e}")
