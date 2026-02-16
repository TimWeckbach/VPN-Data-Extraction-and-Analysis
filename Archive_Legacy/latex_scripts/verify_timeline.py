import pandas as pd

df = pd.read_csv('SSoT_CSVs/Qual_Timeline.csv')
strat_cols = ['Technical Blocking', 'Price Discrimination', 'Content Licensing', 'Regulatory Compliance', 'Legal Threat']
df['Total_Strategic'] = df[strat_cols].sum(axis=1)

years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
print("Year | CL% | RC% | PD% | LT% | TB%")
print("-----|-----|-----|-----|-----|-----")
for y in years:
    row = df[df['Year'] == y]
    if not row.empty and row['Total_Strategic'].iloc[0] > 0:
        total = row['Total_Strategic'].iloc[0]
        cl = round(100 * row['Content Licensing'].iloc[0] / total, 1)
        rc = round(100 * row['Regulatory Compliance'].iloc[0] / total, 1)
        pd_val = round(100 * row['Price Discrimination'].iloc[0] / total, 1)
        lt = round(100 * row['Legal Threat'].iloc[0] / total, 1)
        tb = round(100 * row['Technical Blocking'].iloc[0] / total, 1)
        print(f"{y} | {cl} | {rc} | {pd_val} | {lt} | {tb}")
