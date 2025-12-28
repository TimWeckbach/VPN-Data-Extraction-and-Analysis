import pandas as pd

file_path = r'Quantitative DATA\sheet1_raw.csv'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # UK Fix: Lines 54 and 55
    if line.startswith('United Kingdom ['):
        parts = line.split(',')
        # Col 4: Netflix £12.99 -> £10.99
        # Col 6: Disney+ £14.99 -> £10.99
        # Col 9: Apple Music £16.99 -> £10.99
        parts[4] = '£10.99'
        parts[6] = '£10.99'
        parts[9] = '£10.99'
        lines[i] = ','.join(parts)
        
    if '↳ USD Equivalent' in line and i > 0 and 'United Kingdom' in lines[i-1]:
        parts = line.split(',')
        # Rate is 1.27
        # 10.99 * 1.27 = 13.96
        parts[4] = '$13.96'
        parts[6] = '$13.96'
        parts[9] = '$13.96'
        lines[i] = ','.join(parts)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated UK prices for Netflix, Disney+, and Apple Music to match Individual plans.")
