import csv

file_path = r'Quantitative DATA\sheet1_raw.csv'

rows = []
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Find UK row
for i, row in enumerate(rows):
    if len(row) > 0 and 'United Kingdom [' in row[0]:
        # Indices:
        # 0: Country
        # 1: Source
        # 2: Salary
        # 3: CoL Index (should be 69.4)
        # 4: Netflix
        # 5: Youtube
        # 6: Disney+
        # 7: Prime
        # 8: Spotify
        # 9: Apple Music
        
        row[3] = '69.4'
        row[4] = '£10.99'
        row[5] = '£12.99'  # Correct UK Individual price
        row[6] = '£10.99'
        row[7] = '£8.99'   # Correct UK Prime Monthly
        row[8] = '£11.99'  # Correct UK Spotify Individual
        row[9] = '£10.99'
        print(f"Fixed UK row values at index {i}")
        
        # Fixed the following row (USD Equivalent) if it exists
        if i + 1 < len(rows) and '↳ USD Equivalent' in rows[i+1][0]:
            rate = 1.27
            rows[i+1][4] = f'${(10.99 * rate):.2f}'
            rows[i+1][5] = f'${(12.99 * rate):.2f}'
            rows[i+1][6] = f'${(10.99 * rate):.2f}'
            rows[i+1][7] = f'${(8.99 * rate):.2f}'
            rows[i+1][8] = f'${(11.99 * rate):.2f}'
            rows[i+1][9] = f'${(10.99 * rate):.2f}'
            print(f"Fixed UK USD Equivalent values at index {i+1}")

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
