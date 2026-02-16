import pandas as pd

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\Thesis_Results_Final.csv"
# No header in CSV, providing names
cols = ['year', 'company', 'doc_type', 'text', 'category', 'score', 'source']
df = pd.read_csv(file_path, names=cols)

print("--- Data Distribution by Year ---")
year_counts = df['year'].value_counts().sort_index()
print(year_counts)

print("\n--- Data for 2025 ---")
df_2025 = df[df['year'] == 2025]
print(f"Total entries in 2025: {len(df_2025)}")
print("Companies covered in 2025:")
print(df_2025['company'].unique())

print("\n--- Data for 2023 ---")
df_2023 = df[df['year'] == 2023]
print(f"Total entries in 2023: {len(df_2023)}")
