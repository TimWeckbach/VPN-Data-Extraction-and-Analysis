import pandas as pd

df = pd.read_csv('SSoT_CSVs/Qual_Timeline.csv')
strat_cols = ['Content Licensing', 'Regulatory Compliance', 'Legal Threat', 'Price Discrimination', 'Technical Blocking', 'Security Risk', 'Privacy/Security', 'Legitimate Portability', 'User Workaround']
# These are the main ones plotted in Fig 4.7 usually

df['Total_Strategic'] = df[['Technical Blocking', 'Price Discrimination', 'Content Licensing', 'Regulatory Compliance', 'Legal Threat', 'Account Action', 'Privacy/Security', 'Security Risk', 'Legitimate Portability', 'User Workaround']].sum(axis=1)

for col in strat_cols:
    coords = []
    for year in sorted(df['Year'].unique()):
        if year < 2020: continue
        row = df[df['Year'] == year]
        if not row.empty and row['Total_Strategic'].iloc[0] > 0:
            val = round(100 * row[col].iloc[0] / row['Total_Strategic'].iloc[0], 1)
            coords.append(f'({year},{val})')
    
    print(f'% {col}')
    print(f'\\addplot coordinates {" ".join(coords)};')
