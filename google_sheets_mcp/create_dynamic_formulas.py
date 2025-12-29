
import gspread
from google.oauth2.credentials import Credentials
import os
import sys
import time

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = "1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk"
TOKEN_FILE = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\google_sheets_mcp\token_personal.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

SERVICES = ["Microsoft", "Youtube Premium", "Spotify", "Adobe", "Netflix", "Disney+", "Amazon Prime", "Apple Music", "ExpressVPN", "NordVPN"]
CATEGORIES = ["Technical Blocking", "Price Discrimination", "Content Licensing", "Regulatory Compliance", "Legal Threat", "Account Action", "Privacy/Security", "Security Risk", "Legitimate Portability", "User Workaround", "General Terms"]
YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

def main():
    print("--- GENERATING EXPLICIT CELL-LEVEL FORMULAS ---")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)

    def get_ws(name, rows=1200, cols=20):
        try:
            ws = sh.worksheet(name)
            ws.clear()
            return ws
        except gspread.WorksheetNotFound:
            return sh.add_worksheet(title=name, rows=rows, cols=cols)

    # --- 1. Qual_Counts ---
    print(" - Qual_Counts...")
    ws = get_ws("Qual_Counts")
    rows = [["Category", "Count", "Percent"]]
    for i, cat in enumerate(CATEGORIES):
        r = i + 2
        rows.append([
            cat, 
            f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$D:$D, A{r})', 
            f'=IF(SUM($B$2:$B$11)>0, B{r}/SUM($B$2:$B$11), 0)'
        ])
    ws.update(range_name='A1', values=rows, value_input_option='USER_ENTERED')
    ws.format('C2:C11', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}})

    # --- 2. Qual_Timeline ---
    print(" - Qual_Timeline...")
    ws = get_ws("Qual_Timeline")
    header = ["Year"] + CATEGORIES
    data = [header]
    for r_idx, year in enumerate(YEARS):
        row_num = r_idx + 2
        row_data = [year]
        for c_idx in range(len(CATEGORIES)):
            col_letter = chr(ord('B') + c_idx)
            # Count where Year=Year and Category=Header
            formula = f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$A:$A, $A{row_num}, DATA_CATEGORIZED_GEMINI_3!$D:$D, {col_letter}$1)'
            row_data.append(formula)
        data.append(row_data)
    ws.update(range_name='A1', values=data, value_input_option='USER_ENTERED')

    # --- 3. Service_Stats ---
    print(" - Service_Stats...")
    ws = get_ws("Service_Stats")
    header = ["Service"] + CATEGORIES
    data = [header]
    for r_idx, srv in enumerate(SERVICES):
        row_num = r_idx + 2
        row_data = [srv]
        for c_idx in range(len(CATEGORIES)):
            col_letter = chr(ord('B') + c_idx)
            formula = f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$B:$B, $A{row_num}, DATA_CATEGORIZED_GEMINI_3!$D:$D, {col_letter}$1)'
            row_data.append(formula)
        data.append(row_data)
    ws.update(range_name='A1', values=data, value_input_option='USER_ENTERED')

    # --- 4. Timeline_Details (Explicit Rows) ---
    print(" - Timeline_Details...")
    ws = get_ws("Timeline_Details")
    # This tab is the one the user specifically complained about.
    # We will generate a row for every Year/Service/Category combination.
    # Every data cell will be a formula.
    header = ["Year", "Service", "Category", "Count", "Percentage"]
    data = [header]
    current_row = 2
    for yr in YEARS:
        for srv in SERVICES:
            for cat in CATEGORIES:
                # Count
                f_count = f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$A:$A, $A{current_row}, DATA_CATEGORIZED_GEMINI_3!$B:$B, "{srv}", DATA_CATEGORIZED_GEMINI_3!$D:$D, "{cat}")'
                # Percentage
                f_pct = f'=IF(SUMIFS($D:$D, $A:$A, $A{current_row}, $B:$B, "{srv}")>0, D{current_row}/SUMIFS($D:$D, $A:$A, $A{current_row}, $B:$B, "{srv}"), 0)'
                data.append([yr, srv, cat, f_count, f_pct])
                current_row += 1
    ws.update(range_name=f'A1:E{len(data)}', values=data, value_input_option='USER_ENTERED')
    ws.format('E2:E1200', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}})

    # --- 5. Service_Evolution ---
    print(" - Service_Evolution...")
    ws = get_ws("Service_Evolution")
    matrix = [["" for _ in range(12)] for _ in range(150)]
    curr = 0
    for srv in SERVICES:
        matrix[curr][0] = f"{srv} Live Table"
        matrix[curr+1] = ["Year"] + CATEGORIES
        for r_idx, yr in enumerate(YEARS):
            row_num = curr + 3 + r_idx
            row_data = [yr]
            for c_idx in range(len(CATEGORIES)):
                col_letter = chr(ord('B') + c_idx)
                formula = f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$B:$B, "{srv}", DATA_CATEGORIZED_GEMINI_3!$A:$A, $A{row_num}, DATA_CATEGORIZED_GEMINI_3!$D:$D, {col_letter}${curr+2})'
                row_data.append(formula)
            matrix[curr+2+r_idx] = row_data
        curr += 14
    ws.update(range_name='A1', values=matrix, value_input_option='USER_ENTERED')

    # --- 6. Correlation_Data ---
    print(" - Correlation_Data...")
    ws = get_ws("Correlation_Data")
    rows = [["Service", "Price Discrimination Score", "Enforcement Intensity"]]
    enf_cats = ["Technical Blocking", "Legal Threat", "Account Action"]
    
    # Mapping for DSPI Data (Short Name -> DSPI Name)
    dspi_map = {
        "Adobe": "Adobe Creative Cloud",
        "Microsoft": "Microsoft 365"
    }

    for i, srv in enumerate(SERVICES):
        r = i + 2
        # Use mapped name if exists, else match the service name
        dspi_name = dspi_map.get(srv, srv)
        
        stdev = f'=STDEV(FILTER(DSPI_Data!$J:$J, DSPI_Data!$B:$B = "{dspi_name}"))'
        # Total formulas
        total = f'COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$B:$B, "{srv}")' # Use exact Service name from Qual
        enf_sum = "+".join([f'COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$B:$B, "{srv}", DATA_CATEGORIZED_GEMINI_3!$D:$D, "{c}")' for c in enf_cats])
        intensity = f'=IF({total}>0, ({enf_sum})/{total}, 0)'
        rows.append([srv, stdev, intensity])
    ws.update(range_name='A1', values=rows, value_input_option='USER_ENTERED')
    ws.format('C2:C11', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}})

    # --- 7. Deep_Dive_Stats ---
    print(" - Deep_Dive_Stats...")
    ws = get_ws("Deep_Dive_Stats")
    ws.update_acell('A1', "Relative Category Share per Year (%)")
    
    data = [["Year"] + CATEGORIES]
    for r_idx, yr in enumerate(YEARS):
        row_num = r_idx + 3
        row_data = [yr]
        for c_idx in range(len(CATEGORIES)):
            col_letter = chr(ord('B') + c_idx)
            # Qual_Timeline header is at B1. Data for 2016 is at row 2.
            # We explicitly divide the count by the year total.
            formula = f'=IF(SUM(Qual_Timeline!$B{r_idx+2}:$K{r_idx+2})>0, Qual_Timeline!{col_letter}{r_idx+2}/SUM(Qual_Timeline!$B{r_idx+2}:$K{r_idx+2}), 0)'
            row_data.append(formula)
        data.append(row_data)
    ws.update(range_name='A2', values=data, value_input_option='USER_ENTERED')
    ws.format('B3:K12', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}})

    # --- 8. Dashboard_Stats ---
    print(" - Dashboard_Stats...")
    ws = get_ws("Dashboard_Stats")
    ws.update_acell('A1', "Company Distribution")
    rows = [["Company", "Total Clauses"]]
    for i, srv in enumerate(SERVICES):
        rows.append([srv, f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$B:$B, $A{i+3})'])
    ws.update(range_name='A2', values=rows, value_input_option='USER_ENTERED')
    
    ws.update_acell('E1', "Document Type Distribution")
    doc_types = ["10-K/Annual Report", "Transcripts/Investor", "Other/Internal"]
    rows = [["Type", "Total Clauses"]]
    for i, dt in enumerate(doc_types):
        rows.append([dt, f'=COUNTIFS(DATA_CATEGORIZED_GEMINI_3!$F:$F, $E{i+3})'])
    ws.update(range_name='E2', values=rows, value_input_option='USER_ENTERED')

    print("Success! Integrated all dynamic formulas.")

if __name__ == "__main__":
    main()
