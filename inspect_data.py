
import pandas as pd

try:
    df = pd.read_csv(r"Quantitative DATA\sheet1_raw.csv", header=None)
    # Target countries
    countries = ['United States', 'Turkey', 'Argentina', 'Switzerland']
    
    # Target Cols: Country(0), Netflix(4), NordVPN(13), ExpressVPN(14)
    cols = [0, 4, 13, 14]
    
    print("--- Data Inspection ---")
    for idx, row in df.iterrows():
        c = str(row[0])
        # Check if row is one of our targets
        if any(x in c for x in countries) and "Rate:" not in c and "USD Equivalent" not in c:
            print(f"Row {idx}: {c}")
            print(f"  Netflix: {row[4]}")
            print(f"  NordVPN: {row[13]}")
            print(f"  ExpVPN:  {row[14]}")
            print("-" * 20)
            
except Exception as e:
    print(e)
