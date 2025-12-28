import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Paths
FIG_DIR = r"Latex Thesis\figures"
DATA_DIR = r"Quantitative DATA"

# Ensure output dir exists
os.makedirs(FIG_DIR, exist_ok=True)

# Exchange rates for calculation if needed (from process_google_sheet_data.py)
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

def load_and_clean_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_DSPI.csv"))
    
    # The CSV contains formulas as strings (e.g. "=D2*F2")
    # We need to evaluate them or replace them with actual values for Matplotlib
    
    # Calculate Price_USD
    df['Price_USD_Value'] = df['Original_Price'] * df['Currency'].map(RATES).fillna(1.0)
    
    # Calculate DSPI
    df['DSPI_Value'] = df['Price_USD_Value'] / df['US_Baseline_Price']
    
    # Calculate Affordability
    df['Affordability_Value'] = df['Price_USD_Value'] / df['Monthly_Salary_USD']
    
    # Calculate Real Difference %
    df['Real_Diff_Pct_Value'] = (df['Price_USD_Value'] - df['US_Baseline_Price']) / df['US_Baseline_Price']
    
    return df

def generate_dspi_heatmap(df):
    print("Generating DSPI Heatmap...")
    pivot = df.pivot_table(index='Country', columns='Service', values='DSPI_Value')
    
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot, cmap="RdYlGn_r", annot=True, fmt=".2f", linewidths=.5)
    plt.title("Global Heatmap of Digital Service Pricing (DSPI)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "dspi_heatmap.pdf"))
    plt.close()

def generate_affordability_heatmap(df):
    print("Generating Affordability Heatmap...")
    pivot = df.pivot_table(index='Country', columns='Service', values='Affordability_Value')
    
    plt.figure(figsize=(14, 10))
    # Multiply by 100 for percentage display in heatmap
    sns.heatmap(pivot * 100, cmap="YlOrRd", annot=True, fmt=".2f", linewidths=.5)
    plt.title("Affordability: Cost as % of Median Monthly Wage")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "affordability_heatmap.pdf"))
    plt.close()

def generate_real_difference_heatmap(df):
    print("Generating Real Difference % Heatmap...")
    pivot = df.pivot_table(index='Country', columns='Service', values='Real_Diff_Pct_Value')
    
    plt.figure(figsize=(14, 10))
    # Multiply by 100 for percentage display
    sns.heatmap(pivot * 100, cmap="RdYlGn_r", annot=True, fmt=".1f", linewidths=.5, center=0)
    plt.title("Real Price Difference vs. US Baseline (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "real_difference_heatmap.pdf"))
    plt.close()

def generate_correlation_plot():
    print("Generating Correlation Scatter...")
    df_corr = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Correlation.csv"))
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_corr, x='Price_Discrimination_Score', y='Enforcement_Intensity_Percent', hue='Service', s=150)
    
    # Add labels
    for i, row in df_corr.iterrows():
        plt.text(row['Price_Discrimination_Score']+0.005, row['Enforcement_Intensity_Percent']+0.5, 
                 row['Service'], fontsize=10, weight='bold')
                 
    plt.title("Price Discrimination vs Enforcement Intensity")
    plt.xlabel("Price Discrimination Score (StdDev DSPI)")
    plt.ylabel("Enforcement Intensity (%)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "protection_vs_pricing.pdf"))
    plt.close()

def generate_timeline_plot():
    print("Generating Timeline...")
    df_time = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Qual_Timeline.csv"))
    df_time = df_time.set_index('Year')
    
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df_time, dashes=False, markers=True, markersize=8, linewidth=2)
    plt.title("Evolution of Strategic Frames (2016-2024)")
    plt.ylabel("Frequency (%)")
    plt.xlabel("Year")
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "category_timeline_all_normalized.pdf"))
    plt.close()

def generate_distribution_bar():
    print("Generating Distribution Bar...")
    df_dist = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Qual_Counts.csv"))
    
    plt.figure(figsize=(10, 7))
    # Sort by percent for better visual
    df_dist = df_dist.sort_values('Percent', ascending=False)
    sns.barplot(data=df_dist, y='Category', x='Percent', palette="viridis")
    plt.title("Proportional Distribution of Enforcement Categories")
    plt.xlabel("Frequency (%)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "service_distribution_ratios.pdf"))
    plt.close()

if __name__ == "__main__":
    df_main = load_and_clean_data()
    
    generate_dspi_heatmap(df_main)
    generate_affordability_heatmap(df_main)
    generate_real_difference_heatmap(df_main)
    generate_correlation_plot()
    generate_timeline_plot()
    generate_distribution_bar()
    
    print(f"All figures regenerated in {FIG_DIR}")
