import gspread
import pandas as pd
import sys
import time

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_col_letter(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def main():
    print("--- Starting Visualization Generation ---")
    
    # Authenticate
    try:
        gc = gspread.service_account(filename="credentials.json", scopes=SCOPES)
        sheet_url = "https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit?usp=sharing"
        sh = gc.open_by_url(sheet_url)
    except Exception as e:
        print(f"Auth/Connection Failed: {e}")
        return

    # 1. READ DATA (Local CSV with Gemini Results)
    csv_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
    print(f"Reading data from '{csv_path}'...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Use Category_Gemini3 (or New_Category) if available
    cat_col = 'Category_Gemini3' if 'Category_Gemini3' in df.columns else 'New_Category'
    if cat_col in df.columns:
        df['Label'] = df[cat_col].fillna(df['Label'])
    
    # Filter out errors and empty
    df = df[~df['Label'].isna() & (df['Label'] != "") & (~df['Label'].str.contains("Error", na=False))]

    # 2. AGGREGATE DATA
    print("Aggregating statistics...")
    
    # A. Company Distribution
    company_counts = df['Company'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']
    
    # B. Doc_Type Distribution
    doctype_counts = df['Doc_Type'].value_counts().reset_index()
    doctype_counts.columns = ['Doc_Type', 'Count']
    
    # C. Top Labels
    # Filter out empty/null labels
    if 'Label' in df.columns:
        label_counts = df[df['Label'] != ""]['Label'].value_counts().head(15).reset_index()
        label_counts.columns = ['Label', 'Count']
    else:
        label_counts = pd.DataFrame(columns=['Label', 'Count'])

    # 3. PREPARE DASHBOARD SHEET
    target_sheet_name = "Dashboard_Stats"
    try:
        ws_dash = sh.worksheet(target_sheet_name)
        print(f"Sheet '{target_sheet_name}' exists. Clearing...")
        ws_dash.clear()
    except gspread.WorksheetNotFound:
        print(f"Creating '{target_sheet_name}'...")
        ws_dash = sh.add_worksheet(title=target_sheet_name, rows=100, cols=20)

    dashboard_id = ws_dash.id

    # 4. UPLOAD AGGREGATED DATA
    # Layout:
    # A1: Company Stats | D1: DocType Stats | G1: Label Stats
    
    # Helper to prepare lists
    def df_to_list(d):
        return [d.columns.values.tolist()] + d.values.tolist()

    # Upload Comp Stats
    ws_dash.update(range_name='A1', values=df_to_list(company_counts))
    comp_len = len(company_counts) + 1
    
    # Upload DocType Stats
    ws_dash.update(range_name='D1', values=df_to_list(doctype_counts))
    doc_len = len(doctype_counts) + 1
    
    # Upload Label Stats
    ws_dash.update(range_name='G1', values=df_to_list(label_counts))
    lbl_len = len(label_counts) + 1

    print("Data uploaded to Dashboard. Creating charts...")

    # 5. CREATE CHARTS via batchUpdate
    # We need to define requests
    
    requests = []
    
    # Chart 1: Company Bar Chart (Anchored at A(comp_len + 2))
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Distribution by Company",
                    "basicChart": {
                        "chartType": "COLUMN",
                        "headerCount": 1,
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Company"},
                            {"position": "LEFT_AXIS", "title": "Count"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 0, "endRowIndex": comp_len, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                        "series": [{"series": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 0, "endRowIndex": comp_len, "startColumnIndex": 1, "endColumnIndex": 2}]}}, "targetAxis": "LEFT_AXIS"}]
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": dashboard_id, "rowIndex": comp_len + 2, "columnIndex": 0},
                        "widthPixels": 600,
                        "heightPixels": 371
                    }
                }
            }
        }
    })

    # Chart 2: DocType Pie Chart (Anchored at E(doc_len + 2))
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Distribution by Document Type",
                    "pieChart": {
                        "legendPosition": "RIGHT_LEGEND",
                        "domain": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 1, "endRowIndex": doc_len, "startColumnIndex": 3, "endColumnIndex": 4}]}},
                        "series": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 1, "endRowIndex": doc_len, "startColumnIndex": 4, "endColumnIndex": 5}]}}
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": dashboard_id, "rowIndex": 1, "columnIndex": 9}, # Shifted to right
                        "widthPixels": 400,
                        "heightPixels": 300
                    }
                }
            }
        }
    })
    
    # Chart 3: Label Bar Chart (Anchored below Company chart)
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Top 15 Labels",
                    "basicChart": {
                        "chartType": "BAR", # Horizontal Bar
                        "headerCount": 1,
                        "legendPosition": "NO_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Count"},
                            {"position": "LEFT_AXIS", "title": "Label"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 0, "endRowIndex": lbl_len, "startColumnIndex": 6, "endColumnIndex": 7}]}}}],
                        "series": [{"series": {"sourceRange": {"sources": [{"sheetId": dashboard_id, "startRowIndex": 0, "endRowIndex": lbl_len, "startColumnIndex": 7, "endColumnIndex": 8}]}}, "targetAxis": "BOTTOM_AXIS"}]
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": dashboard_id, "rowIndex": comp_len + 25, "columnIndex": 0},
                        "widthPixels": 800,
                        "heightPixels": 500
                    }
                }
            }
        }
    })

    # Execute Requests
    try:
        sh.batch_update({"requests": requests})
        print("Charts created successfully!")
    except Exception as e:
        print(f"Error creating charts: {e}")

if __name__ == "__main__":
    main()
