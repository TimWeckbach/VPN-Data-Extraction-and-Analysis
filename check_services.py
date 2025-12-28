import pandas as pd

df = pd.read_csv(r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master.csv")
print("Services:", df['Company'].unique())
print("Categories:", df['Category_Gemini3'].unique())
