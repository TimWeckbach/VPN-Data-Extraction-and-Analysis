import pandas as pd

excel_path = r'C:\Users\Titan\Downloads\Digital Services Price Index (DSPI).xlsx'
xl = pd.ExcelFile(excel_path)
df = xl.parse('Sheet1')

target_countries = [
    'Germany', 'United Kingdom', 'Turkey', 'Pakistan', 'Brazil', 
    'Philippines', 'Argentina', 'Ukraine', 'Poland', 'United States', 'Switzerland'
]

for country in target_countries:
    print(f"\n--- {country} ---")
    mask = df.iloc[:,0].str.contains(country, case=False, na=False)
    matches = df[mask].index.tolist()
    rows = []
    for m in matches:
        rows.extend([m, m+1])
    if rows:
        # Print Country name, Amazon Prime (col 4), and Adobe (col 11)
        print(df.iloc[rows, [0, 4, 11]])
