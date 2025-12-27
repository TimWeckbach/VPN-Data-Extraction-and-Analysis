import os.path
import gspread
from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Initialize FastMCP
mcp = FastMCP("GoogleWorkspaceMCP")

# SCOPES
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations'
]

# Account Tokens
# Map descriptive names to file paths
ACCOUNTS = {
    "default": "token_personal.json",         # gruenerspecht44
    "secondary": "token_second_private.json" # weckbach.t
}

def get_creds(account_name="default"):
    """
    Gets valid user credentials for the specified account.
    Defaults to 'default' (gruenerspecht44).
    """
    token_file = ACCOUNTS.get(account_name)
    if not token_file:
        raise ValueError(f"Unknown account: {account_name}. Available: {list(ACCOUNTS.keys())}")
        
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token back
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception:
                 raise RuntimeError(f"Token expired and refresh failed for {account_name}. Re-run setup.")
        else:
            raise RuntimeError(f"No valid token found for {account_name}. Please run auth setup.")

    return creds

def get_service(api_name, api_version, account_name="default"):
    creds = get_creds(account_name)
    return build(api_name, api_version, credentials=creds)

# --- TOOLS ---

@mcp.tool()
def read_recent_emails(account: str = "default", max_results: int = 5):
    """
    Read recent emails.
    Args:
        account: "default" (gruenerspecht44) or "secondary" (weckbach.t)
        max_results: number of emails
    """
    try:
        service = get_service('gmail', 'v1', account)
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        data = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            data.append({'id': msg['id'], 'subject': subject, 'snippet': txt.get('snippet')})
        return data
    except Exception as e:
        return f"Error accessing Gmail for '{account}': {str(e)}"

@mcp.tool()
def list_drive_files(account: str = "default", page_size: int = 10):
    """List files in Google Drive for the specified account."""
    service = get_service('drive', 'v3', account)
    results = service.files().list(
        pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
    return results.get('files', [])

@mcp.tool()
def list_calendar_events(account: str = "default", max_results: int = 10):
    """List upcoming calendar events for the specified account."""
    try:
        import datetime
        service = get_service('calendar', 'v3', account)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return [{'start': event['start'].get('dateTime', event['start'].get('date')), 'summary': event['summary']} for event in events]
    except Exception as e:
        return f"Error accessing Calendar: {str(e)}"

# Wrappers for Sheets/Docs similar to above... (abbreviated for this update to focus on multi-account)
@mcp.tool()
def read_sheet(url: str, worksheet: str = None, account: str = "default"):
    """Read a Google Sheet using the specified account."""
    creds = get_creds(account)
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(url)
    ws = sh.worksheet(worksheet) if worksheet else sh.sheet1
    return ws.get_all_records()

if __name__ == "__main__":
    mcp.run()
