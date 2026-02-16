
import pandas as pd
import re

df = pd.read_csv('Thesis_Dataset_Master.csv')
adobe_2020 = df[(df['Company'] == 'Adobe') & (df['Year'] == 2020)]

print(f"Adobe 2020 rows: {len(adobe_2020)}")
sentences = adobe_2020['Sentence'].astype(str).tolist()

for i, s in enumerate(sentences):
    if "item" in s.lower():
        print(f"Line {i}: {s}")
