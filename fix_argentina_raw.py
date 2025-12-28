import pandas as pd

file_path = r'Quantitative DATA\sheet1_raw.csv'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 107 is index 106
lines[106] = lines[106].replace('[Rate: 1 ARS = 0.0012 USD]', '[Rate: 1 ARS = 0.0012 USD / 1 BRL = 0.2 USD]')
# Line 108 is index 107. We want to change the value at NordVPN column (Index 13).
# The line is: "    ↳ USD Equivalent,,,,$18.00,$5.02,$14.76,$9.54,$3.96,$0.01,$44.64,$35.40,$10.80,$0.26,$0.12,"
# We replace $0.26 with $42.60
lines[107] = lines[107].replace('$0.26', '$42.60')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated sheet1_raw.csv")
