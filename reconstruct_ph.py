import pandas as pd

# Load the messy CSV
# We need to skip the header if it's metadata, or just load everything as strings.
file_path = r'Quantitative DATA\sheet1_raw.csv'

# Since the file is messy (mixed headers, etc.), I'll manually fix the lines in memory and then write back.
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Let's fix line 146 (index 145) and 147 (index 146)
# Target state for Philippines:
# Col 11 (Adobe): "PHP 3800"
# Col 13 (NordVPN): "PHP 4800"

ph_line = lines[145].split(',')
# We need to find the correct column indices.
# Col 0: Country
# Col 1, 2, 3: Metadata
# Col 4: Netflix
# Col 11: Adobe (Photography)
# Col 12: Xbox
# Col 13: NordVPN
# Col 14: ExpressVPN

# Recounting indices based on line 146 output:
# [0] Philippines... [1] [2] [3] 31.9 [4] 449 PHP [5] ₱189/month [6] ₱249 [7] ₱149 [8] ₱169 [9] ₱139 [10] ₱4,899.00 [11] Adobe [12] Xbox [13] NordVPN [14] ExpressVPN

# Let's just reconstruct the whole line correctly.
ph_base = ['Philippines [Rate: 1 PHP = 0.018 USD]', '', '', '31.9', '449 PHP', '₱189/month', '₱249', '₱149', '₱169', '₱139', '"₱4,899.00"', 'PHP 3800', '₱320', 'PHP 4800', '$97.72', 'https://www.yugatech.com/software/netflix-hbo-max-amazon-prime-video-disney-plus-vs-apple-tv-plus-2025-comparison/']
lines[145] = ','.join(ph_base) + '\n'

ph_usd_base = ['', '', '', '', '$8.08', '$3.40', '$4.48', '$2.68', '$3.04', '$2.50', '$88.18', '$68.40', '$5.76', '$86.40', '$97.72', '']
lines[146] = ','.join(ph_usd_base) + '\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Reconstructed Philippines row in sheet1_raw.csv correctly.")
