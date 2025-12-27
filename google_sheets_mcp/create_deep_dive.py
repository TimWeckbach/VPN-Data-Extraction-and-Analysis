import gspread
import pandas as pd
import sys
import numpy as np

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    print("--- Generating Deep Dive Visualizations ---")
    
    # 1. SETUP
    try:
        gc = gspread.service_account(filename="credentials.json", scopes=SCOPES)
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit?usp=sharing")
        
        # Read Data from LOCAL CSV (latest Gemini results)
        csv_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
        df = pd.read_csv(csv_path)
        
        # Clean Data
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
        df = df[(df['Year'] >= 2016) & (df['Year'] <= 2025)]
        
        # Use New_Category (Gemini results) as the primary Label
        # Fill missing with original Label if Gemini haven't reached it yet
        df['Label'] = df['New_Category'].fillna(df['Label'])
        
        # Clean Labels (ignore empty and errors)
        df = df[~df['Label'].isna() & (df['Label'] != "") & (~df['Label'].str.contains("Error", na=False))]
        
    except Exception as e:
        print(f"Setup Failed: {e}")
        return

    # 2. ANALYSIS LOGIC
    
    # A. "Global Evolution of Topics" (Year vs Top 5 Categories)
    top_categories = df['Label'].value_counts().head(7).index.tolist()
    df_top = df[df['Label'].isin(top_categories)]
    
    pivot_topics_time = df_top.pivot_table(index='Year', columns='Label', values='Sentence', aggfunc='count', fill_value=0)
    pivot_topics_time.reset_index(inplace=True)
    
    # B. "Company Priorities" (Company vs Category Heatmap-ish)
    # We normalized by row (Company) to see %, e.g. "Spotify is 40% Content Licensing"
    pivot_comp_cat = df.pivot_table(index='Company', columns='Label', values='Sentence', aggfunc='count', fill_value=0)
    # Keep only relevant categories (Top 10) to make chart readable
    top_10_cats = df['Label'].value_counts().head(10).index.tolist()
    pivot_comp_cat = pivot_comp_cat[top_10_cats]
    
    # Convert to percentage
    pivot_comp_cat_pct = pivot_comp_cat.div(pivot_comp_cat.sum(axis=1), axis=0) * 100
    pivot_comp_cat_pct = pivot_comp_cat_pct.round(1).fillna(0)
    pivot_comp_cat_pct.reset_index(inplace=True)

    # 3. UPLOAD AND CHART
    sheet_name = "Deep_Dive_Stats"
    try:
        # Delete existing sheet to remove old charts/data completely
        ws = sh.worksheet(sheet_name)
        sh.del_worksheet(ws)
        print(f"Deleted old '{sheet_name}'...")
    except gspread.WorksheetNotFound:
        pass
        
    print(f"Creating new '{sheet_name}'...")
    ws = sh.add_worksheet(title=sheet_name, rows=200, cols=30)
    
    sheet_id = ws.id
    
    requests = []
    current_row = 1
    
    # --- CHART 1: TOPIC EVOLUTION (Stacked Area) ---
    ws.update(range_name=f'A{current_row}', values=[["TOPIC EVOLUTION: How the focus changed over time (Top 7 Categories)"]])
    current_row += 2
    
    # Data Upload
    headers_1 = pivot_topics_time.columns.tolist()
    rows_1 = pivot_topics_time.values.tolist()
    ws.update(range_name=f'A{current_row}', values=[headers_1] + rows_1)
    
    # Chart Spec
    # Columns: A=Year, B...H=Categories
    series_list = []
    # FIX: internal API is 0-indexed. 
    # current_row is 1-based. 
    # Header is at current_row (index current_row-1).
    header_idx = current_row - 1
    
    for i in range(1, len(headers_1)):
        series_list.append({
            "series": {
                "sourceRange": {
                    "sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + len(rows_1) + 1, "startColumnIndex": i, "endColumnIndex": i+1}]
                }
            },
            "targetAxis": "LEFT_AXIS"
        })
        
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Topic Evolution (2016-2025): Relative Category Share",
                    "basicChart": {
                        "chartType": "AREA",
                        "headerCount": 1,
                        "stackedType": "PERCENT_STACKED",
                        "legendPosition": "RIGHT_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Year"},
                            {"position": "LEFT_AXIS", "title": "% Share of Provisions"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + len(rows_1) + 1, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                        "series": series_list
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": sheet_id, "rowIndex": header_idx, "columnIndex": len(headers_1) + 1},
                        "widthPixels": 800,
                        "heightPixels": 450
                    }
                }
            }
        }
    })
    
    current_row += len(rows_1) + 25 # Move down
    
    # --- CHART 2: STRATEGIC FOCUS by COMPANY (100% Stacked Bar) ---
    ws.update(range_name=f'A{current_row}', values=[["STRATEGIC FOCUS: What each company prioritizes (% of their terms)"]])
    current_row += 2
    
    headers_2 = pivot_comp_cat_pct.columns.tolist()
    rows_2 = pivot_comp_cat_pct.values.tolist()
    ws.update(range_name=f'A{current_row}', values=[headers_2] + rows_2)
    
    # Chart Spec
    series_list_2 = []
    header_idx_2 = current_row - 1
    
    for i in range(1, len(headers_2)):
        series_list_2.append({
            "series": {
                "sourceRange": {
                    "sources": [{"sheetId": sheet_id, "startRowIndex": header_idx_2, "endRowIndex": header_idx_2 + len(rows_2) + 1, "startColumnIndex": i, "endColumnIndex": i+1}]
                }
            },
            "targetAxis": "LEFT_AXIS"
        })
        
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Strategic Focus by Company (Top 10 Categories)",
                    "basicChart": {
                        "chartType": "COLUMN",
                        "headerCount": 1,
                        "stackedType": "PERCENT_STACKED", # 100% Stacked
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Company"},
                            {"position": "LEFT_AXIS", "title": "Percentage of Terms"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx_2, "endRowIndex": header_idx_2 + len(rows_2) + 1, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                        "series": series_list_2
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": sheet_id, "rowIndex": header_idx_2 + len(rows_2) + 2, "columnIndex": 0}, # Below table
                        "widthPixels": 900,
                        "heightPixels": 500
                    }
                }
            }
        }
    })
    
    try:
        sh.batch_update({"requests": requests})
        print("Deep Dive Charts created successfully on 'Deep_Dive_Stats'!")
    except Exception as e:
        print(f"Error creating charts: {e}")

if __name__ == "__main__":
    main()
