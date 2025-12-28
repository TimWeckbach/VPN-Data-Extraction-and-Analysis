import pandas as pd

file_path = r'Quantitative DATA\sheet1_raw.csv'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Philippines Fix: Line 146
    if line.startswith('Philippines ['):
        parts = line.split(',')
        # Col 11 (Adobe): "฿1.425,42" -> "PHP 3,800"
        # Col 13 (NordVPN): "HK$629" -> "PHP 4,800"
        parts[11] = '"PHP 3,800"'
        parts[13] = '"PHP 4,800"'
        lines[i] = ','.join(parts)
        
    if '↳ USD Equivalent' in line and i > 0 and 'Philippines' in lines[i-1]:
        parts = line.split(',')
        # Rate: 0.018
        # 3800 * 0.018 = 68.4
        # 4800 * 0.018 = 86.4
        parts[11] = '$68.40'
        parts[13] = '$86.40'
        lines[i] = ','.join(parts)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated Philippines Adobe and NordVPN prices to PHP and fixed calculations.")
