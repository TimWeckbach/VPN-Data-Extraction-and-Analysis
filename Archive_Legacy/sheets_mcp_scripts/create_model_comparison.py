import gspread
import pandas as pd
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def main():
    print("--- Generating Model Comparison Charts (Gemini vs BERT) ---")
    
    # 1. Connect
    try:
        gc = gspread.service_account(filename="credentials.json", scopes=SCOPES)
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit?usp=sharing")
    except Exception as e:
        print(f"Auth Failed: {e}")
        return

    # 2. Read Data
    csv_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_BERT.csv"
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    # Clean Filter
    # Filter out empty or Error categories
    df = df[
        (df['New_Category'].notna()) & (df['New_Category'] != "") & (~df['New_Category'].str.contains("Error", na=False)) &
        (df['BERT_Category'].notna()) & (df['BERT_Category'] != "")
    ]
    
    print(f"Analyzing {len(df)} overlapping valid rows...")

    # 3. Calculate Distribution
    dist_gemini = df['New_Category'].value_counts(normalize=True).reset_index()
    dist_gemini.columns = ['Category', 'Gemini_Pct']
    dist_gemini['Gemini_Pct'] *= 100
    
    dist_bert = df['BERT_Category'].value_counts(normalize=True).reset_index()
    dist_bert.columns = ['Category', 'BERT_Pct']
    dist_bert['BERT_Pct'] *= 100
    
    # Merge
    dist_all = pd.merge(dist_gemini, dist_bert, on='Category', how='outer').fillna(0)
    dist_all = dist_all.sort_values('Gemini_Pct', ascending=False)

    # 4. Calculate Agreement per Category
    # For each category defined by Gemini, how often did BERT agree?
    agreement_data = []
    
    categories = df['New_Category'].unique()
    for cat in categories:
        sub = df[df['New_Category'] == cat]
        total = len(sub)
        agreed = len(sub[sub['BERT_Category'] == cat])
        pct = (agreed / total) * 100 if total > 0 else 0
        agreement_data.append({'Category': cat, 'Agreement_Pct': pct, 'Count_Gemini': total})
        
    df_agree = pd.DataFrame(agreement_data).sort_values('Count_Gemini', ascending=False)

    # 5. Prepare Sheet
    sheet_name = "Model_Comparison"
    try:
        ws = sh.worksheet(sheet_name)
        sh.del_worksheet(ws)
    except gspread.WorksheetNotFound:
        pass
        
    ws = sh.add_worksheet(title=sheet_name, rows=100, cols=20)
    sheet_id = ws.id
    
    current_row = 1
    requests = []

    # --- SECTION 1: DISTRIBUTION ---
    ws.update(range_name=f'A{current_row}', values=[["CATEGORY DISTRIBUTION: Gemini vs BERT (%)"]])
    current_row += 2
    
    headers_1 = dist_all.columns.tolist() # Category, Gemini_Pct, BERT_Pct
    values_1 = dist_all.values.tolist()
    
    ws.update(range_name=f'A{current_row}', values=[headers_1] + values_1)
    
    # Chart 1: Clustered Column
    header_idx = current_row - 1
    num_rows = len(values_1)
    
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Category Distribution Comparison",
                    "basicChart": {
                        "chartType": "COLUMN",
                        "legendPosition": "RIGHT_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Category"},
                            {"position": "LEFT_AXIS", "title": "Percentage of Dataset"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + num_rows + 1, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                        "series": [
                            {"series": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + num_rows + 1, "startColumnIndex": 1, "endColumnIndex": 2}]}}, "targetAxis": "LEFT_AXIS"},
                            {"series": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx, "endRowIndex": header_idx + num_rows + 1, "startColumnIndex": 2, "endColumnIndex": 3}]}}, "targetAxis": "LEFT_AXIS"}
                        ]
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": sheet_id, "rowIndex": current_row + num_rows + 2, "columnIndex": 0},
                        "widthPixels": 800,
                        "heightPixels": 400
                    }
                }
            }
        }
    })
    
    # --- SECTION 2: AGREEMENT ---
    current_row += num_rows + 25 
    ws.update(range_name=f'A{current_row}', values=[["AGREEMENT RATE: When Gemini says 'X', does BERT agree?"]])
    current_row += 2
    
    headers_2 = ['Category', 'Gemini_Count', 'BERT_Agreement_Pct']
    values_2 = df_agree[['Category', 'Count_Gemini', 'Agreement_Pct']].values.tolist()
    
    ws.update(range_name=f'A{current_row}', values=[headers_2] + values_2)
    
    header_idx_2 = current_row - 1
    num_rows_2 = len(values_2)
    
    # Chart 2: Bar Chart of Agreement
    requests.append({
        "addChart": {
            "chart": {
                "spec": {
                    "title": "Agreement Rate per Category (Gemini Baseline)",
                    "basicChart": {
                        "chartType": "BAR",
                        "legendPosition": "NO_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "% Agreement"},
                            {"position": "LEFT_AXIS", "title": "Category"}
                        ],
                        "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx_2, "endRowIndex": header_idx_2 + num_rows_2 + 1, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                        "series": [
                            {"series": {"sourceRange": {"sources": [{"sheetId": sheet_id, "startRowIndex": header_idx_2, "endRowIndex": header_idx_2 + num_rows_2 + 1, "startColumnIndex": 2, "endColumnIndex": 3}]}}, "targetAxis": "BOTTOM_AXIS"}
                        ]
                    }
                },
                "position": {
                    "overlayPosition": {
                        "anchorCell": {"sheetId": sheet_id, "rowIndex": current_row + num_rows_2 + 2, "columnIndex": 0},
                        "widthPixels": 800,
                        "heightPixels": 400
                    }
                }
            }
        }
    })
    
    sh.batch_update({"requests": requests})
    print("Comparison charts created on 'Model_Comparison' sheet.")

if __name__ == "__main__":
    main()
