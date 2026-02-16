import os
import glob
import pandas as pd
import gspread
import time

def main():
    # 1. Setup connection
    print("Connecting to Google Sheets...")
    try:
        gc = gspread.service_account(filename="credentials.json")
        sheet_url = "https://docs.google.com/spreadsheets/d/1lxlStc4uYO2LbvUHqG4men-egRdvGJ_drgVWPSCqOxk/edit?usp=sharing"
        sh = gc.open_by_url(sheet_url)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Find all CSV files in the parent directories
    # based on the user's workspace structure
    base_dir = os.path.dirname(os.getcwd()) # Go up one level from google_sheets_mcp
    search_pattern = os.path.join(base_dir, "**", "*.csv")
    csv_files = glob.glob(search_pattern, recursive=True)
    
    print(f"Found {len(csv_files)} CSV files.")

    for file_path in csv_files:
        try:
            filename = os.path.basename(file_path)
            # Sheet names usually have a limit (100 chars? 30 chars? gsheets is loose but good to be safe)
            # and no special chars like : \ / ? * [ ]
            clean_name = filename.replace(".csv", "")[:50] 
            
            print(f"Processing: {filename} -> Sheet: '{clean_name}'")
            
            # Read CSV
            df = pd.read_csv(file_path)
            # Handle NaN values because JSON/Google Sheets doesn't like them
            df = df.fillna("")
            
            # Prepare data: header + rows
            data = [df.columns.values.tolist()] + df.values.tolist()
            
            # Get or Create Worksheet
            try:
                ws = sh.worksheet(clean_name)
                print(f"  - Sheet '{clean_name}' exists. Clearing content...")
                ws.clear()
            except gspread.WorksheetNotFound:
                print(f"  - Creating new sheet '{clean_name}'...")
                ws = sh.add_worksheet(title=clean_name, rows=100, cols=20)
            
            # Update data
            # block update is faster
            ws.update(range_name='A1', values=data)
            print("  - Upload complete.")
            
            # Sleep briefly to avoid hitting rate limits too hard
            time.sleep(1.5)

        except Exception as e:
            print(f"  - Error uploading {filename}: {e}")

    print("\nAll files processed.")

if __name__ == "__main__":
    main()
