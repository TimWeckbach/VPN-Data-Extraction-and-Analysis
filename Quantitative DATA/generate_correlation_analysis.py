
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Paths
TOS_DATA_PATH = r"Quantitative DATA\Thesis_Dataset_Master_RiskFactorsOnly.csv"
DSPI_DATA_PATH = r"Quantitative DATA\dspi_raw_data.csv"
OUTPUT_DIR = r"Latex Thesis\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_correlation_analysis():
    print("Loading data...")
    # Load Classification Data
    if not os.path.exists(TOS_DATA_PATH):
        print(f"Error: {TOS_DATA_PATH} not found.")
        return
    tos_df = pd.read_csv(TOS_DATA_PATH)
    
    # Load Price Data
    if not os.path.exists(DSPI_DATA_PATH):
        print(f"Error: {DSPI_DATA_PATH} not found.")
        return
    price_df = pd.read_csv(DSPI_DATA_PATH)
    
    # --- 1. Calculate Protection Score (Enforcement Intensity) ---
    # Metric: % of clauses that are "Technical Blocking", "Account Action", or "Content Licensing"
    # We aggregate by Service.
    
    # Normalize Service Names in ToS
    # Expected in ToS: Netflix, Disney+, Spotify, Apple, Microsoft, Amazon, etc.
    # Expected in DSPI: Netflix, Disney+, Spotify, Apple Music, Microsoft 365, Steam (AAA Game)
    
    # Rename "Company" to "Service" to match DSPI data for easier merging
    tos_df.rename(columns={'Company': 'Service'}, inplace=True)
    
    name_map_tos = {
        'Apple': 'Apple Music',
        'Microsoft': 'Microsoft 365',
        'Steam': 'Steam (AAA Game)',
        'Amazon Prime': 'Amazon', 
    }
    tos_df['Service'] = tos_df['Service'].replace(name_map_tos)
    
    # Filter for the relevant detected categories
    protection_categories = ['Technical Blocking', 'Account Action', 'Content Licensing']
    
    # Calculate Total Sentences per Service
    total_counts = tos_df.groupby('Service').size().reset_index(name='Total_Sentences')
    
    # Calculate Protection Sentences per Service
    protection_df = tos_df[tos_df['New_Category'].isin(protection_categories)]
    protection_counts = protection_df.groupby('Service').size().reset_index(name='Protection_Sentences')
    
    # Merge and Calculate Ratio
    enforcement_df = pd.merge(total_counts, protection_counts, on='Service', how='left').fillna(0)
    enforcement_df['Protection_Score'] = enforcement_df['Protection_Sentences'] / enforcement_df['Total_Sentences'] * 100
    
    print("Enforcement Scores calculated:")
    print(enforcement_df[['Service', 'Protection_Score']])

    # --- 2. Calculate Price Discrimination Score ---
    # Metric: Coefficient of Variation (CV) of DSPI or Standard Deviation
    # CV = StdDev / Mean. Since Mean is close to 1, StdDev is fine.
    # Higher StdDev means more "Tiered" pricing across the world.
    
    price_stats = price_df.groupby('Service')['DSPI'].agg(['std', 'mean']).reset_index()
    price_stats['Price_Discrimination_Score'] = price_stats['std']
    
    print("\nPrice Stats:")
    print(price_stats)

    # --- 3. Merge and Correlate ---
    merged_df = pd.merge(enforcement_df, price_stats, on='Service', how='inner')
    
    if merged_df.empty:
        print("Error: No common services found between datasets after name mapping.")
        print(f"ToS Services: {enforcement_df['Service'].unique()}")
        print(f"Price Services: {price_stats['Service'].unique()}")
        return

    print("\nMerged Data for Correlation:")
    print(merged_df)
    
    # Calculate Correlation
    corr = merged_df['Protection_Score'].corr(merged_df['Price_Discrimination_Score'])
    print(f"\nCorrelation Coefficient (R): {corr}")

    # --- 4. Plot ---
    plt.figure(figsize=(10, 7))
    sns.set_style("whitegrid")
    
    # Scatter plot
    sns.scatterplot(
        data=merged_df, 
        x='Price_Discrimination_Score', 
        y='Protection_Score', 
        s=200, 
        color='#2c3e50'
    )
    
    # Add labels
    for i, row in merged_df.iterrows():
        plt.text(
            row['Price_Discrimination_Score'] + 0.01, 
            row['Protection_Score'] + 0.5, 
            row['Service'], 
            fontsize=12,
            weight='bold'
        )

    # Trend line
    sns.regplot(
        data=merged_df, 
        x='Price_Discrimination_Score', 
        y='Protection_Score', 
        scatter=False, 
        color='#e74c3c',
        line_kws={'linestyle':'--'}
    )

    plt.title(f'Strategic Alignment: Price Discrimination vs. Protective Enforcement\n(Pearson R = {corr:.2f})', fontsize=14, weight='bold')
    plt.xlabel('Price Inconsistency (Std. Dev of Global DSPI)', fontsize=12)
    plt.ylabel('Enforcement Intensity\n(% of Terms focused on Blocking/Licensing)', fontsize=12)
    
    # Add quadrant annotations (implied)
    # plt.axvline(x=merged_df['Price_Discrimination_Score'].mean(), color='gray', linestyle=':', alpha=0.5)
    # plt.axhline(y=merged_df['Protection_Score'].mean(), color='gray', linestyle=':', alpha=0.5)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'protection_vs_pricing.pdf')
    plt.savefig(output_path)
    print(f"Saved correlation plot to {output_path}")

if __name__ == "__main__":
    generate_correlation_analysis()
