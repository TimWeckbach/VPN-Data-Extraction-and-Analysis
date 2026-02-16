import pandas as pd
df = pd.read_csv('Thesis_Dataset_Master_Redefined.csv')
with open('companies.txt', 'w') as f:
    for company in df['Company'].unique():
        f.write(f"{company}\n")
