import pandas as pd
import numpy as np
import os

print("--- STARTING PIPELINE AUDIT ---")

# 1. Load Data
try:
    dspi = pd.read_csv("Quantitative DATA/Sheets_Import_DSPI.csv")
    qual_counts = pd.read_csv("Quantitative DATA/Sheets_Import_Qual_Counts.csv")
    qual_timeline = pd.read_csv("Quantitative DATA/Sheets_Import_Qual_Timeline.csv")
    correlation = pd.read_csv("Quantitative DATA/Sheets_Import_Correlation.csv")
    print("[PASS] All CSV files loaded.")
except Exception as e:
    print(f"[FAIL] Could not load CSVs: {e}")
    exit(1)

# 2. Check for API Errors in Categorization
# The Sheets_Import_Qual_Counts.csv typically aggregates them. Let's check if 'Error' appears in the Category column.
errors = qual_counts[qual_counts['Category'].str.contains("Error", case=False, na=False)]
if not errors.empty:
    print(f"[WARN] Found API Errors in Categorization Results:\n{errors}")
else:
    print("[PASS] No explicit 'Error' categories found in summarized counts.")

# 3. Verify DSPI Calculation Logic
# DSPI = Price_USD / US_Price_USD
# We need to infer US price. Let's pick 'Netflix' 'United States'.
us_netflix = dspi[(dspi['Service'] == 'Netflix') & (dspi['Country'] == 'United States')]
if not us_netflix.empty:
    us_price = us_netflix.iloc[0]['Price_USD']
    # Pick a test row: Netflix Turkey
    turkey_netflix = dspi[(dspi['Service'] == 'Netflix') & (dspi['Country'] == 'Turkey')]
    if not turkey_netflix.empty:
        tk_price = turkey_netflix.iloc[0]['Price_USD']
        tk_dspi = turkey_netflix.iloc[0]['DSPI']
        
        expected_dspi = tk_price / us_price
        if abs(tk_dspi - expected_dspi) < 0.01:
            print(f"[PASS] DSPI Logic Verified (Netflix TR: {tk_dspi} vs Exp {expected_dspi:.4f})")
        else:
            print(f"[FAIL] DSPI Logic Mismatch! (Netflix TR: {tk_dspi} vs Exp {expected_dspi:.4f})")
else:
    print("[WARN] Could not find US Netflix row for DSPI verification.")

# 4. Verify Affordability Logic
# Affordability = Price_USD / Median_Wage (converted to USD) ? 
# Or is it Local_Price / Local_Wage? The column is Affordability_Wage_Based_%
# Let's check for reasonable bounds (0 to 100%).
invalid_affordability = dspi[(dspi['Affordability_Wage_Based_%'] < 0) | (dspi['Affordability_Wage_Based_%'] > 100)]
if invalid_affordability.empty:
    print(f"[PASS] All Affordability percentages are within valid bounds (0-100%). Max found: {dspi['Affordability_Wage_Based_%'].max():.2f}%")
else:
    print(f"[FAIL] Found invalid Affordability values:\n{invalid_affordability}")

# 5. Verify Correlation Re-Calculation
# Correlation between Price_Discrimination_Score (StdDev of DSPI usually?) and Enforcement_Intensity_Percent
calc_corr = correlation['Price_Discrimination_Score'].corr(correlation['Enforcement_Intensity_Percent'])
print(f"[INFO] Audit Calculated Correlation: {calc_corr:.4f}")

# Check against the -0.36 figure
if -0.40 <= calc_corr <= -0.32:
     print(f"[PASS] Correlation matches reported range (-0.36 approx).")
else:
     print(f"[WARN] Correlation ({calc_corr:.4f}) deviates from reported -0.36.")

print("--- AUDIT COMPLETE ---")
