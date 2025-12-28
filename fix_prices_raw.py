import pandas as pd

file_path = r'Quantitative DATA\sheet1_raw.csv'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Argentina Row: Apple Music and NordVPN
    if line.startswith('Argentina ['):
        parts = line.split(',')
        # Col 9 (Apple Music): "5.978" -> "5978"
        parts[9] = parts[9].replace('5.978', '5978')
        # Col 13 (NordVPN): "213 BRL" (already done but let's be sure)
        # parts[13] = "213 BRL"
        lines[i] = ','.join(parts)
        
    # Argentina USD Equivalent row (usually follows Argentina)
    if '↳ USD Equivalent' in line and i > 0 and 'Argentina' in lines[i-1]:
        parts = line.split(',')
        # Col 9 (Apple Music): Based on 5978 * 0.0012 = 7.17
        parts[9] = '$7.17'
        lines[i] = ','.join(parts)

    # Pakistan Row: Amazon Prime
    if line.startswith('Pakistan ['):
        parts = line.split(',')
        # Col 7 (Amazon Prime): "₹299" -> "PKR 599"
        parts[7] = 'PKR 599'
        lines[i] = ','.join(parts)
        
    if '↳ USD Equivalent' in line and i > 0 and 'Pakistan' in lines[i-1]:
        parts = line.split(',')
        # Col 7 (Amazon Prime): 599 * 0.0036 = 2.16
        parts[7] = '$2.16'
        lines[i] = ','.join(parts)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated sheet1_raw.csv with Apple Music Argentina and Amazon Prime Pakistan fixes.")
