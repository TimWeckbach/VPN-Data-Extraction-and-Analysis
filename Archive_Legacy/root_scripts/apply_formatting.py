import gspread
from google.oauth2.credentials import Credentials
import os

# Configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit"
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def main():
    print("--- APPLYING CONDITIONAL FORMATTING ---")
    
    # 1. Authenticate
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: Token file not found at {TOKEN_FILE}")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    gc = gspread.authorize(creds)
    
    # 2. Open Sheet
    print(f"Opening Sheet: {SHEET_URL}")
    try:
        sh = gc.open_by_url(SHEET_URL)
        ws = sh.worksheet("DSPI_Data")
    except Exception as e:
        print(f"Error opening sheet or tab: {e}")
        return

    # 3. Define Conditional Formatting Rules using batch_update
    # We want Red (High) to Green (Low) or vice versa?
    # Context: "outlier" usually means expensive or cheap.
    # Typically: Green = Good (Cheap), Red = Bad (Expensive).
    
    # Column I: DSPI (Index 8, 0-based) -> Row 2 to 1000
    # Column K: Affordability (Index 10) -> Row 2 to 1000
    
    # GridRange is 0-indexed.
    # I = 8
    # K = 10
    
    requests = [
        # Rule 1: DSPI (Column I)
        # Low Value (Green) -> Mid -> High Value (Red)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": ws.id,
                            "startRowIndex": 1,
                            "endRowIndex": 200,
                            "startColumnIndex": 8,
                            "endColumnIndex": 9
                        }
                    ],
                    "gradientRule": {
                        "minpoint": {
                            "color": {"green": 1, "red": 0.35, "blue": 0.35}, # Light Green
                            "type": "MIN"
                        },
                        "midpoint": {
                            "color": {"green": 1, "red": 1, "blue": 1}, # White
                            "type": "PERCENTILE",
                            "value": "50"
                        },
                        "maxpoint": {
                            "color": {"green": 0.35, "red": 1, "blue": 0.35}, # Light Red
                            "type": "MAX"
                        }
                    }
                },
                "index": 0
            }
        },
        # Rule 2: Affordability (Column K)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": ws.id,
                            "startRowIndex": 1,
                            "endRowIndex": 200,
                            "startColumnIndex": 10,
                            "endColumnIndex": 11
                        }
                    ],
                    "gradientRule": {
                         "minpoint": {
                            "color": {"green": 1, "red": 0.35, "blue": 0.35}, # Light Green (Affordable)
                            "type": "MIN"
                        },
                        "midpoint": {
                            "color": {"green": 1, "red": 1, "blue": 1}, # White
                            "type": "PERCENTILE",
                            "value": "50"
                        },
                        "maxpoint": {
                            "color": {"green": 0.35, "red": 1, "blue": 0.35}, # Light Red (Expensive)
                            "type": "MAX"
                        }
                    }
                },
                "index": 1
            }
        },
        # Rule 3: Real Difference (Column L)
        # Negative (Save money) -> Green
        # Positive (Pay more) -> Red
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": ws.id,
                            "startRowIndex": 1,
                            "endRowIndex": 200,
                            "startColumnIndex": 11,
                            "endColumnIndex": 12
                        }
                    ],
                    "gradientRule": {
                         "minpoint": {
                            "color": {"green": 1, "red": 0.35, "blue": 0.35}, # Green (Big Savings)
                            "type": "MIN"
                        },
                        "midpoint": {
                            "color": {"green": 1, "red": 1, "blue": 1}, # White
                            "type": "NUMBER",
                            "value": "0"
                        },
                        "maxpoint": {
                            "color": {"green": 0.35, "red": 1, "blue": 0.35}, # Red (Surcharge)
                            "type": "MAX"
                        }
                    }
                },
                "index": 2
            }
        },
        # Rule 4: Real Difference % (Column M)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": ws.id,
                            "startRowIndex": 1,
                            "endRowIndex": 200,
                            "startColumnIndex": 12,
                            "endColumnIndex": 13
                        }
                    ],
                    "gradientRule": {
                         "minpoint": {
                            "color": {"green": 1, "red": 0.35, "blue": 0.35}, # Green (Big Savings)
                            "type": "MIN"
                        },
                        "midpoint": {
                            "color": {"green": 1, "red": 1, "blue": 1}, # White
                            "type": "NUMBER",
                            "value": "0"
                        },
                        "maxpoint": {
                            "color": {"green": 0.35, "red": 1, "blue": 0.35}, # Red (Surcharge)
                            "type": "MAX"
                        }
                    }
                },
                "index": 3
            }
        },
        # FORMATTING: Real Difference % as PERCENT
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 1,
                    "endRowIndex": 200,
                    "startColumnIndex": 12,
                    "endColumnIndex": 13
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "PERCENT",
                            "pattern": "0.00%"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        }
    ]

    try:
        sh.batch_update({"requests": requests})
        print("Success! Conditional formatting applied to DSPI_Data.")
    except Exception as e:
        print(f"Failed to apply formatting: {e}")

if __name__ == "__main__":
    main()
