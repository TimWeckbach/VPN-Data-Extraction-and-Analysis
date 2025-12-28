
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk" 
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICES = ["Microsoft", "Youtube Premium", "Spotify", "Adobe", "Netflix", "Disney+", "Amazon Prime", "Apple Music", "ExpressVPN", "NordVPN"]

def main():
    print("--- REBUILDING CHARTS ON THEIR DATA SHEETS (EXPLICIT ALIGNMENT) ---")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)

    sheet_ids = {ws.title: ws.id for ws in sh.worksheets()}
    target_tabs = ["Qual_Counts", "Qual_Timeline", "Service_Evolution", "Correlation_Data", "Dashboard_Stats", "Service_Stats", "Deep_Dive_Stats", "Timeline_Details"]
    
    # Clear existing charts
    for name in target_tabs:
        if name in sheet_ids:
            meta = service.spreadsheets().get(spreadsheetId=SHEET_ID, ranges=[name]).execute()
            sheets = meta.get('sheets', [])
            if sheets and 'charts' in sheets[0]:
                service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": [{"deleteEmbeddedObject": {"objectId": c['chartId']}} for c in sheets[0]['charts']]}).execute()

    requests = []

    # 1. Qual_Counts (Bar)
    tid = sheet_ids["Qual_Counts"]
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Strategic Frames Distribution", "basicChart": {"chartType": "BAR", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": 1, "endColumnIndex": 2}]}}}]}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 0, "columnIndex": 3}, "widthPixels": 600, "heightPixels": 400}}}}
    })

    # 2. Qual_Timeline (Line) - Headers A1:K1, Data A2:A11
    # EXCLUDING the last column (General Terms) if it makes the chart unreadable, or keeping it?
    # User said: "make a grpah of that (that exludes the general temrs of course)"
    # My previous change added "General Terms" to the data. It is likely the LAST column.
    # Columns are: B=Tech Blocking ... K=User Workaround, L=General Terms (if 11 cols).
    # Range used: startCol 1 to 11. 1=B, 11=L. 
    # If General Terms is the 11th category (index 10 in list, so column L?), I need to be careful.
    # Let's check CATEGORIES list in create_dynamic_formulas.py: 
    # [Tech, Price, Content, Reg, Legal, Account, Priv, Sec, Port, User, General] -> 11 items.
    # Columns: A=Year, B=Tech, ..., K=User, L=General.
    # Chart logic: range(1, 11) means cols 1 (B) up to 10 (K). 
    # Python range(1, 11) is 1, 2, ..., 10.
    # So it covers B, C, D, E, F, G, H, I, J, K.
    # It STOPS before 11 (L). 
    # So "General Terms" (Col L) is ALREADY EXCLUDED by the range(1, 11) logic!
    # I will verify this and keep it as is.
    
    tid = sheet_ids["Qual_Timeline"]
    series = [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": i, "endColumnIndex": i+1}]}}} for i in range(1, 11)]
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Evolution of Strategic Frames (Excl. General Terms)", "basicChart": {"chartType": "LINE", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": series}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 12, "columnIndex": 0}, "widthPixels": 900, "heightPixels": 500}}}}
    })

    # 3. Service_Evolution (Stacked Bars)
    tid = sheet_ids["Service_Evolution"]
    for i, srv in enumerate(SERVICES):
        r = i * 14
        series = [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": r+1, "endRowIndex": r+12, "startColumnIndex": c, "endColumnIndex": c+1}]}}} for c in range(1, 11)]
        requests.append({
            "addChart": {"chart": {"spec": {"title": f"{srv}: Multi-Year Evolution", "basicChart": {"chartType": "COLUMN", "stackedType": "STACKED", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": r+1, "endRowIndex": r+12, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": series}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": r, "columnIndex": 12}, "widthPixels": 600, "heightPixels": 380}}}}
        })

    # 4. Deep_Dive_Stats (Topic Evolution - Area) - Headers A2:K2, Data A3:K12
    tid = sheet_ids["Deep_Dive_Stats"]
    series = [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 12, "startColumnIndex": c, "endColumnIndex": c+1}]}}} for c in range(1, 11)]
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Global Priority Shift (%)", "basicChart": {"chartType": "AREA", "stackedType": "PERCENT_STACKED", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 12, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": series}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 14, "columnIndex": 0}, "widthPixels": 900, "heightPixels": 550}}}}
    })

    # 5. Service_Stats (Strategic Focus - 100% Stacked) - Headers A1:K1, Data A2:K11
    tid = sheet_ids["Service_Stats"]
    series = [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": c, "endColumnIndex": c+1}]}}} for c in range(1, 11)]
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Company Priority Mix (%)", "basicChart": {"chartType": "COLUMN", "stackedType": "PERCENT_STACKED", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": series}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 12, "columnIndex": 0}, "widthPixels": 900, "heightPixels": 550}}}}
    })

    # 6. Dashboard_Stats - Headers A2:B2 and E2:F2
    tid = sheet_ids["Dashboard_Stats"]
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Company Volume", "basicChart": {"chartType": "COLUMN", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 12, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": [{"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 12, "startColumnIndex": 1, "endColumnIndex": 2}]}}}]}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 14, "columnIndex": 0}, "widthPixels": 500, "heightPixels": 350}}}}
    })
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Document Types", "pieChart": {"domain": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 10, "startColumnIndex": 4, "endColumnIndex": 5}]}}, "series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 10, "startColumnIndex": 5, "endColumnIndex": 6}]}}}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid, "rowIndex": 1, "columnIndex": 8}}}}}
    })

    # 7. Timeline_Details (Evolution Graph on the Details sheet)
    # Using 'Qual_Timeline' data (aggregated) for the chart, but displaying it on 'Timeline_Details'
    tid_details = sheet_ids["Timeline_Details"]
    tid_source = sheet_ids["Qual_Timeline"]
    series = [{"series": {"sourceRange": {"sources": [{"sheetId": tid_source, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": i, "endColumnIndex": i+1}]}}} for i in range(1, 11)] # Cols B-K (Excludes L=General Terms)
    requests.append({
        "addChart": {"chart": {"spec": {"title": "Evolution of Strategic Frames (Summary)", "basicChart": {"chartType": "LINE", "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": tid_source, "startRowIndex": 0, "endRowIndex": 11, "startColumnIndex": 0, "endColumnIndex": 1}]}}}], "series": series}}, "position": {"overlayPosition": {"anchorCell": {"sheetId": tid_details, "rowIndex": 1, "columnIndex": 6}, "widthPixels": 800, "heightPixels": 500}}}}
    })

    service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": requests}).execute()
    print("Success! Integrated all charts with localized data.")

if __name__ == "__main__":
    main()
