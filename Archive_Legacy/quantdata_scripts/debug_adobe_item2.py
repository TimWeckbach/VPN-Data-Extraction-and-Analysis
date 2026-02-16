
import pandas as pd

df = pd.read_csv('Thesis_Dataset_Master.csv')
adobe_2020 = df[(df['Company'] == 'Adobe') & (df['Year'] == 2020)]

sentences = adobe_2020['Sentence'].astype(str).tolist()

for i, s in enumerate(sentences):
    if "item 2" in s.lower() or "properties" in s.lower():
        print(f"Line {i}: {s}")
