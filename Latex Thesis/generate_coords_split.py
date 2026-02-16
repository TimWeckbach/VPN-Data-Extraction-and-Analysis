import pandas as pd
import os

df = pd.read_csv('SSoT_CSVs/Service_Stats.csv')
strat_cols = ['Content Licensing', 'Regulatory Compliance', 'Legal Threat', 'Price Discrimination', 'Technical Blocking', 'Security Risk', 'Privacy/Security', 'Legitimate Portability', 'User Workaround']
df['Total_Strategic'] = df[strat_cols].sum(axis=1)
order = ['Adobe', 'Amazon Prime', 'Apple Music', 'Disney+', 'ExpressVPN', 'Microsoft', 'Netflix', 'NordVPN', 'Spotify', 'Youtube Premium']

os.makedirs('coords', exist_ok=True)
for i, col in enumerate(strat_cols):
    coords = []
    for service in order:
        row = df[df['Service'] == service]
        if not row.empty and row['Total_Strategic'].iloc[0] > 0:
            val = round(100 * row[col].iloc[0] / row['Total_Strategic'].iloc[0], 1)
            coords.append(f'({val},{service})')
        else:
            coords.append(f'(0.0,{service})')
    
    with open(f'coords/col_{i}.txt', 'w') as f:
        f.write(" ".join(coords))
