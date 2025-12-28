import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import time

# Configuration
SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk" # Master Sheet
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    print("--- CREATING CHARTS IN GOOGLE SHEETS ---")
    
    # 1. Authenticate
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)

    # Get Sheet IDs for the tabs (needed for API calls)
    sheet_ids = {ws.title: ws.id for ws in sh.worksheets()}
    
    # Clear existing charts first to avoid duplicates
    for sheet_name, sheet_id in sheet_ids.items():
        if sheet_name in ["Correlation_Data", "Qual_Timeline", "Qual_Counts"]:
            print(f"Clearing existing charts from {sheet_name}...")
            # Get existing charts
            try:
                # We need to get the sheet metadata to find chart IDs
                # This requires a separate read call per sheet or a get entry
                # Simpler approach: blindly try to delete charts if we had their IDs? No.
                # Use sh.values_get? No, we need spreadsheet.get
                
                # Fetch sheet metadata including charts
                sheet_metadata = service.spreadsheets().get(spreadsheetId=SHEET_ID, ranges=[sheet_name]).execute()
                sheets = sheet_metadata.get('sheets', [])
                if sheets:
                    charts = sheets[0].get('charts', [])
                    if charts:
                         delete_requests = []
                         for c in charts:
                             delete_requests.append({
                                 "deleteEmbeddedObject": {
                                     "objectId": c['chartId']
                                 }
                             })
                         if delete_requests:
                             service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": delete_requests}).execute()
                             print(f" - Deleted {len(delete_requests)} old charts.")
            except Exception as e:
                print(f"Warning: Could not clear charts from {sheet_name}: {e}")

    requests = []

    # --- CHART 1: Correlation Scatter Plot ---
    # Data: 'Correlation_Data'!A:C
    # X-Axis: Price_Discrimination_Score (Col B)
    # Y-Axis: Enforcement_Intensity_Percent (Col C)
    # Series: Service Names (Col A) - Labels
    
    if "Correlation_Data" in sheet_ids:
        tid = sheet_ids["Correlation_Data"]
        print(f"Adding Correlation Scatter Plot to 'Correlation_Data' (ID: {tid})...")
        
        requests.append({
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Price Discrimination vs Enforcement Intensity",
                        "basicChart": {
                            "chartType": "SCATTER",
                            "legendPosition": "RIGHT_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Price Discrimination Score (StdDev of DSPI)"},
                                {"position": "LEFT_AXIS", "title": "Enforcement Intensity (%)"}
                            ],
                            "domains": [{
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": tid,
                                            "startRowIndex": 1,
                                            "endRowIndex": 12, # Approx rows
                                            "startColumnIndex": 1, # Col B
                                            "endColumnIndex": 2   # Col C (Exclusive? No, range is B:B)
                                        }]
                                    }
                                }
                            }],
                            "series": [{
                                "series": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": tid,
                                            "startRowIndex": 1,
                                            "endRowIndex": 12,
                                            "startColumnIndex": 2, # Col C (Y-Axis)
                                            "endColumnIndex": 3
                                        }]
                                    }
                                },
                                "targetAxis": "LEFT_AXIS"
                            }],
                            # Add labels if possible (Bubble chart hack or data labels)
                            # Google Sheets Scatter doesn't easily support point labels via API in BasicChart
                            # We stick to simple scatter for now.
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": tid, "rowIndex": 0, "columnIndex": 5}, # Place at F1
                            "widthPixels": 600,
                            "heightPixels": 400
                        }
                    }
                }
            }
        })

    # --- CHART 2: Timeline Line Chart ---
    # Data: 'Qual_Timeline'!A:K
    # X-Axis: Year (Col A)
    # Series: All Categories (B onwards)
    
    if "Qual_Timeline" in sheet_ids:
        tid = sheet_ids["Qual_Timeline"]
        print(f"Adding Timeline Chart to 'Qual_Timeline' (ID: {tid})...")
        
        requests.append({
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Evolution of Strategic Frames (2016-2024)",
                        "basicChart": {
                            "chartType": "LINE",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Year"},
                                {"position": "LEFT_AXIS", "title": "Frequency (%)"}
                            ],
                            "domains": [{
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": tid,
                                            "startRowIndex": 1,
                                            "endRowIndex": 10,
                                            "startColumnIndex": 0, # Col A (Year)
                                            "endColumnIndex": 1
                                        }]
                                    }
                                }
                            }],
                            "series": [
                                {"series": {"sourceRange": {"sources": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 10, "startColumnIndex": i, "endColumnIndex": i+1}]}}, "targetAxis": "LEFT_AXIS"}
                                for i in range(1, 10) # 9 Series roughly
                            ],
                            "headerCount": 0 # Use first row as headers?
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": tid, "rowIndex": 12, "columnIndex": 0}, # Place below data
                            "widthPixels": 800,
                            "heightPixels": 500
                        }
                    }
                }
            }
        })
        
    # --- CHART 3: Qualifying Counts Pie/Bar ---
    # Data: 'Qual_Counts'!A:B
    if "Qual_Counts" in sheet_ids:
        tid = sheet_ids["Qual_Counts"]
        print(f"Adding Counts Chart to 'Qual_Counts' (ID: {tid})...")
        
        requests.append({
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Distribution of Strategic Frames (Total)",
                        "basicChart": {
                            "chartType": "BAR", # Horizontal Bar
                            "legendPosition": "NO_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Count"},
                                {"position": "LEFT_AXIS", "title": "Category"}
                            ],
                            "domains": [{
                                "domain": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": tid,
                                            "startRowIndex": 1,
                                            "endRowIndex": 12,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 1
                                        }]
                                    }
                                }
                            }],
                            "series": [{
                                "series": {
                                    "sourceRange": {
                                        "sources": [{
                                            "sheetId": tid,
                                            "startRowIndex": 1,
                                            "endRowIndex": 12,
                                            "startColumnIndex": 1,
                                            "endColumnIndex": 2
                                        }]
                                    }
                                }
                            }]
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": tid, "rowIndex": 0, "columnIndex": 3},
                            "widthPixels": 600,
                            "heightPixels": 400
                        }
                    }
                }
            }
        })

    # Execute Batch Update
    if requests:
        body = {
            "requests": requests
        }
        response = service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
        print(f"Success! Created {len(response.get('replies'))} charts.")
    else:
        print("No charts to create (Tabs missing?).")

if __name__ == "__main__":
    main()
