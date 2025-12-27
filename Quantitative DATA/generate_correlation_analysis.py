
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Paths
# Paths
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
        'Amazon': 'Amazon Prime',
        'Adobe': 'Adobe Creative Cloud', # Match Pricing Data Name
    }
    tos_df['Service'] = tos_df['Service'].replace(name_map_tos)
    
    # Duplicate Microsoft ToS data for Xbox Game Pass (they share the Microsoft Services Agreement)
    xbox_rows = tos_df[tos_df['Service'] == 'Microsoft 365'].copy()
    xbox_rows['Service'] = 'Xbox Game Pass'
    tos_df = pd.concat([tos_df, xbox_rows], ignore_index=True)
    
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
        return

    # Define Categories
    cat_map = {
        'Netflix': 'Content Provider (Target)',
        'Disney+': 'Content Provider (Target)', 
        'Spotify': 'Content Provider (Target)',
        'Apple Music': 'Content Provider (Target)',
        'Youtube Premium': 'Content Provider (Target)',
        'Amazon Prime': 'Content Provider (Target)',
        'Xbox Game Pass': 'Content Provider (Target)', # Added Xbox
        'Microsoft 365': 'Utility Software',
        'Adobe Creative Cloud': 'Utility Software',
        'NordVPN': 'VPN Enabler (Adversary)',
        'ExpressVPN': 'VPN Enabler (Adversary)'
    }
    merged_df['Category'] = merged_df['Service'].map(cat_map).fillna('Other')

    print("\nMerged Data for Correlation:")
    print(merged_df)
    
    # Calculate Correlation (Global)
    corr_global = merged_df['Protection_Score'].corr(merged_df['Price_Discrimination_Score'])
    
    # Calculate Correlation (Content Only)
    content_df = merged_df[merged_df['Category'] == 'Content Provider (Target)']
    corr_content = content_df['Protection_Score'].corr(content_df['Price_Discrimination_Score'])
    
    print(f"\nGlobal Correlation (R): {corr_global}")
    print(f"Content Sector Correlation (R): {corr_content}")

    # --- 4. Plot ---
    plt.figure(figsize=(11, 8))
    sns.set_style("whitegrid")
    
    # Scatter plot with categories
    # Palette: Red for Content (Coercive), Blue for Utility, Green for VPN (Open)
    palette = {
        'Content Provider (Target)': '#e74c3c', # Red
        'Utility Software': '#3498db',         # Blue
        'VPN Enabler (Adversary)': '#2ecc71'   # Green
    }
    
    sns.scatterplot(
        data=merged_df, 
        x='Price_Discrimination_Score', 
        y='Protection_Score', 
        hue='Category',
        style='Category',
        palette=palette,
        s=300, 
        alpha=0.9
    )
    
    # Add labels
    for i, row in merged_df.iterrows():
        plt.text(
            row['Price_Discrimination_Score'] + 0.02, 
            row['Protection_Score'] + 0.2, 
            row['Service'], 
            fontsize=11,
            weight='bold'
        )

    # Trend line for Content Providers Only (to show the main thesis point)
    sns.regplot(
        data=content_df, 
        x='Price_Discrimination_Score', 
        y='Protection_Score', 
        scatter=False, 
        color='#c0392b',
        line_kws={'linestyle':'--', 'label': f'Content Trend (R={corr_content:.2f})'}
    )

    plt.title(f'Adversarial Alignment: Content Fortress vs. VPN Enablers', fontsize=16, weight='bold')
    plt.xlabel('Price Discrimination Intensity (Std. Dev of Global DSPI)', fontsize=12)
    plt.ylabel('Enforcement Intensity\n(% of Terms focused on Blocking/Licensing)', fontsize=12)
    plt.legend(title='Strategic Role', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'protection_vs_pricing.pdf')
    plt.savefig(output_path)
    print(f"Saved correlation plot to {output_path}")

if __name__ == "__main__":
    generate_correlation_analysis()
