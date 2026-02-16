import pandas as pd

df = pd.read_csv(r'c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\SSoT_CSVs\Service_Stats.csv')
strat_cols = ['Content Licensing', 'Regulatory Compliance', 'Legal Threat', 'Price Discrimination', 'Technical Blocking', 'Security Risk', 'Privacy/Security', 'Legitimate Portability', 'User Workaround']
colors = ['blue!60', 'orange!60', 'red!60', 'green!60', 'gray!60', 'brown!60', 'purple!60', 'yellow!60', 'teal!60']

df['Total_Strategic'] = df[strat_cols].sum(axis=1)
order = ['Adobe', 'Amazon Prime', 'Apple Music', 'Disney+', 'ExpressVPN', 'Microsoft', 'Netflix', 'NordVPN', 'Spotify', 'Youtube Premium']

for col, color in zip(strat_cols, colors):
    coords = []
    for service in order:
        row = df[df['Service'] == service]
        if not row.empty and row['Total_Strategic'].iloc[0] > 0:
            val = round(100 * row[col].iloc[0] / row['Total_Strategic'].iloc[0], 1)
            coords.append(f'({val},{service})')
        else:
            coords.append(f'(0.0,{service})')
    
    print(f'            % {col}')
    print(f'            \\addplot[fill={color}] coordinates {" ".join(coords)};')
