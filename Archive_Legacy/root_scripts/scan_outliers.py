import pandas as pd

file_path = r'Quantitative DATA\dspi_raw_data.csv'
df = pd.read_csv(file_path)

RATES = {
    'EUR': 1.09, 'USD': 1.0, 'GBP': 1.27, 'CHF': 1.13,
    'TRY': 0.032, 'ARS': 0.0012, 'INR': 0.012, 'BRL': 0.20,
    'JPY': 0.0067, 'CAD': 0.74, 'AUD': 0.66, 'MXN': 0.059,
    'PLN': 0.25, 'ZAR': 0.053, 'COP': 0.00026, 'EGP': 0.021,
    'IDR': 0.000064, 'VND': 0.000041, 'PHP': 0.018, 'THB': 0.028,
    'MYR': 0.21, 'SGD': 0.74, 'HKD': 0.13, 'KRW': 0.00075,
    'CLP': 0.0011, 'PEN': 0.27, 'NGN': 0.0007, 'PKR': 0.0036,
    'UAH': 0.026, 'HUF': 0.0028, 'CZK': 0.043, 'DKK': 0.15, 'NOK': 0.096, 'SEK': 0.096,
    'ILS': 0.27, 'SAR': 0.27, 'AED': 0.27, 'RON': 0.22, 'BGN': 0.55
}

df['Price_USD_Actual'] = df['Original_Price'] * df['Currency'].map(RATES).fillna(1.0)
df['DSPI_Actual'] = df['Price_USD_Actual'] / df['US_Baseline_Price']

print("--- POTENTIAL OUTLIERS (DSPI > 1.4 or DSPI < 0.25) ---")
outliers = df[(df['DSPI_Actual'] > 1.4) | (df['DSPI_Actual'] < 0.25)]
print(outliers[['Service', 'Country', 'Original_Price', 'Currency', 'Price_USD_Actual', 'US_Baseline_Price', 'DSPI_Actual']])

print("\n--- CURRENCY ANOMALIES (USD used in non-US countries with high prices) ---")
# If currency is USD but Original_Price is > 50 in a non-US country that isn't typically USD (like UK/Europe often use local)
# Actually, VPNs ARE often USD. 
anomalies = df[(df['Currency'] == 'USD') & (df['Original_Price'] > 50) & (~df['Country'].isin(['United States', 'USA']))]
print(anomalies[['Service', 'Country', 'Original_Price', 'Currency']])

print("\n--- ZERO OR NEAR-ZERO PRICES ---")
zeros = df[df['Price_USD_Actual'] < 0.1]
print(zeros[['Service', 'Country', 'Original_Price', 'Currency']])
