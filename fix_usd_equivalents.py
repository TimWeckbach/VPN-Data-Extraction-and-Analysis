import pandas as pd
import re

file_path = r'Quantitative DATA\sheet1_raw.csv'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def clean_usd(val):
    return float(re.sub(r'[^\d.]', '', val))

for i, line in enumerate(lines):
    if '↳ USD Equivalent' in line and i > 0:
        prev_line = lines[i-1]
        prev_parts = prev_line.split(',')
        curr_parts = line.split(',')
        
        # Cols 4 to 14 (Services)
        for col_idx in range(4, 15):
            if col_idx >= len(prev_parts) or col_idx >= len(curr_parts): continue
            
            raw_val = prev_parts[col_idx].strip()
            # If the raw value is explicitly $... or USD... or ends with $, it's already USD.
            if raw_val.startswith('$') or 'USD' in raw_val.upper() or raw_val.endswith('$'):
                try:
                    val = clean_usd(raw_val)
                    # The equivalent should be the same as the raw value
                    curr_parts[col_idx] = f'${val:.2f}'
                except:
                    pass
        
        lines[i] = ','.join(curr_parts)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Corrected manually entered 'USD Equivalent' rows for services already priced in USD.")
