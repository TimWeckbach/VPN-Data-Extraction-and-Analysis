import gspread
import pandas as pd
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    print("--- Generatiing Time-Series Visualizations ---")
    
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

    # 2. PROCESS DATA: Time Series
    # Clean Year column
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    # Filter reasonable years (e.g., 2010-2025)
    df = df[(df['Year'] >= 2010) & (df['Year'] <= 2025)]

    # Pivot: Index=Year, Columns=Company, Values=Count
    time_pivot = df.pivot_table(index='Year', columns='Company', values='Sentence', aggfunc='count', fill_value=0)
    time_pivot.reset_index(inplace=True)

    print("Pivot Table Generated:")
    print(time_pivot.head())

    # 3. UPLOAD TO DASHBOARD
    target_sheet_name = "Dashboard_Stats"
    try:
        ws_dash = sh.worksheet(target_sheet_name)
    except gspread.WorksheetNotFound:
        print(f"Error: Target sheet '{target_sheet_name}' not found. Run create_visualizations.py first.")
        return

    dashboard_id = ws_dash.id
    
    # Layout Strategy:
    # We will append this data below the existing charts.
    # Let's say Row 60 (to be safe).
    START_ROW = 60
    
    # Headers
    headers = time_pivot.columns.tolist()
    values = time_pivot.values.tolist()
    
    # Write Title
    ws_dash.update(range_name=f'A{START_ROW-2}', values=[["TIMELINE ANALYSIS: Volume per Service over Years"]])
    
    # Write Data
    ws_dash.update(range_name=f'A{START_ROW}', values=[headers] + values)
    
    print(f"Time-series aggregated data uploaded to Row {START_ROW}.")

    # 4. CREATE CHART (Line Chart)
    # Range: A{START_ROW} to {LastCol}{START_ROW + len(values)}
    
    num_years = len(values)
    num_companies = len(headers) - 1 # Year is col 0
    
    # Requests
    requests = []
    
    # We need to construct series for EACH company
    series_list = []
    for i in range(1, num_companies + 1):
        series_list.append({
            "series": {
                "sourceRange": {
                    "sources": [{
                        "sheetId": dashboard_id, 
                        "startRowIndex": START_ROW, # Skip header (actually startRowIndex is 0-based exclusive of header? No, it's 0-based absolute)
                        # API uses 0-index.
                        # START_ROW is 1-based index in gspread? Yes. 
                        # So Row 60 (1-based) is Index 59.
                        "startRowIndex": START_ROW - 1, 
                        "endRowIndex": START_ROW + num_years, 
                        "startColumnIndex": i, 
                        "endColumnIndex": i+1
                    }]
                }
            },
            "targetAxis": "LEFT_AXIS"
        })

    # Line Chart
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Service Coverage Over Time (Sentences/Provisions Count)",
                    "basicChart": {
                        "chartType": "LINE",
                        "headerCount": 1,
                        "legendPosition": "RIGHT_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Year"},
                            {"position": "LEFT_AXIS", "title": "Volume of Provisions"}
                        ],
                        "domains": [{
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_id, 
                                        "startRowIndex": START_ROW - 1, 
                                        "endRowIndex": START_ROW + num_years, 
                                        "startColumnIndex": 0, # Year Column
                                        "endColumnIndex": 1
                                    }]
                                }
                            }
                        }],
                        "series": series_list
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": dashboard_id, "rowIndex": START_ROW, "columnIndex": num_companies + 2},
                        "widthPixels": 900,
                        "heightPixels": 500
                    }
                }
            }
        }
    })

    try:
        sh.batch_update({"requests": requests})
        print("Time-series chart created successfully!")
    except Exception as e:
        print(f"Error creating chart: {e}")

if __name__ == "__main__":
    main()
