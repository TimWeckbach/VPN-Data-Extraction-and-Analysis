import openpyxl
import os

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\tables\Digital Services Price Index (DSPI).xlsx"
output_file = "chart_audit_results.txt"

print(f"Auditing file for UNIQUE chart titles: {file_path}")

try:
    wb = openpyxl.load_workbook(file_path, read_only=False, data_only=False)
    
    unique_titles = set()
    presentation_list = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        charts = getattr(ws, 'charts', []) or getattr(ws, '_charts', [])
        
        for chart in charts:
            title = getattr(chart, 'title', "No Title")
            # Handle title being an object
            if title and not isinstance(title, str):
                try:
                    title = title.tx.rich.p[0].r[0].t
                except:
                    try:
                        title = str(title)
                    except:
                        title = "Unreadable Title"
            
            title = title.strip()
            if title and title != "No Title":
                if title not in unique_titles:
                    unique_titles.add(title)
                    presentation_list.append(f"[{sheet_name}] {title}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Total Unique Charts Found: {len(unique_titles)}\n")
        f.write("--------------------------------------------------\n")
        for item in sorted(presentation_list):
            f.write(f"{item}\n")

    print(f"Successfully wrote {len(unique_titles)} unique titles to {output_file}")

except Exception as e:
    print(f"Error auditing Excel file: {e}")
