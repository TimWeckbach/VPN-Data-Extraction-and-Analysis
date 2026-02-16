import pandas as pd
import os

# Paths
base_dir = r'c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis'
master_csv = os.path.join(base_dir, 'Thesis_Dataset_Master_Redefined.csv')
output_csv = os.path.join(base_dir, 'SSoT_CSVs', 'Service_Stats.csv')

print(f"Reading {master_csv}...")
df = pd.read_csv(master_csv)

# Filter for 2020+
print("Filtering for Year >= 2020...")
df_filtered = df[df['Year'] >= 2020]
print(f"Rows before: {len(df)}, Rows after: {len(df_filtered)}")

# Aggregate count by Company (Service) and New_Category
# Map 'Company' to 'Service' locally if needed, but CSV seems to use Company name
# Service_Stats.csv columns: Service, Technical Blocking, Price Discrimination, Content Licensing, Regulatory Compliance, Legal Threat, Account Action, Privacy/Security, Security Risk, Legitimate Portability, User Workaround, General Terms

pivot = df_filtered.pivot_table(index='Company', columns='New_Category', aggfunc='size', fill_value=0)

# Ensure all columns exist
required_cols = [
    'Technical Blocking', 'Price Discrimination', 'Content Licensing', 
    'Regulatory Compliance', 'Legal Threat', 'Account Action', 
    'Privacy/Security', 'Security Risk', 'Legitimate Portability', 
    'User Workaround', 'General Terms'
]

for col in required_cols:
    if col not in pivot.columns:
        pivot[col] = 0

# Reorder columns
pivot = pivot[required_cols]
pivot.index.name = 'Service'

# Save
print(f"Saving to {output_csv}...")
pivot.to_csv(output_csv)
print("Done.")
