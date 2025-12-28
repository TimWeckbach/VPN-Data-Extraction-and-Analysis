import csv

file_path = r'Quantitative DATA\sheet1_raw.csv'

rows = []
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Find UK row
for i, row in enumerate(rows):
    if len(row) > 0 and 'United Kingdom [' in row[0]:
        # Original: ['United Kingdom ...', 'oecd2023wages', '5,715', '69.4', '£12.99', '£12.99', '£14.99', '£8.99', '£12.99', '£16.99', ...]
        # Fix columns 4, 6, 9
        row[4] = '£10.99'
        row[6] = '£10.99'
        row[9] = '£10.99'
        print(f"Fixed UK row at index {i}")
        
        # Also fix the following row (USD Equivalent) if it exists
        if i + 1 < len(rows) and '↳ USD Equivalent' in rows[i+1][0]:
            # Rate 1.27
            # 10.99 * 1.27 = 13.96
            rows[i+1][4] = '$13.96'
            rows[i+1][6] = '$13.96'
            rows[i+1][9] = '$13.96'
            print(f"Fixed UK USD Equivalent at index {i+1}")

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
