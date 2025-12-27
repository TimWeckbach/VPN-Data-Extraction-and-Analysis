
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

OUTPUT_DIR = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_dspi_heatmap():
    # Synthetic Data to match Thesis Findings (DSPI Values relative to US = 1.0)
    # < 1.0 means cheaper, > 1.0 means more expensive
    
    # Load Real Data
    csv_path = r"Quantitative DATA\dspi_raw_data.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    raw_df = pd.read_csv(csv_path)
    
    # Calculate DSPI relative to USA for each service
    # DSPI = Local Price USD / US Price USD (Nominal Comparison for Arbitrage)
    # Note: Thesis text mentions "Arbitrage Incentive" which works on Nominal prices.
    # If the user arbitrageur pays with their Swiss credit card in Turkey, they care about the Nominal difference.
    # Re-calculating DSPI column just in case.
    
    # Pivot to get Matrix: Index=Country, Columns=Service, Values=DSPI
    # We first ensure we have unique entries. (Assuming 2024 data only)
    df = raw_df.pivot(index='Country', columns='Service', values='DSPI')
    
    # Fill missing values if any (e.g. Spotify not in Argentina in our small sample)
    # For heatmap purposes, we can leave as NaN or fill. NaN is better for transparency.
    
    # Sort by average DSPI to have cheaper countries at the bottom
    df['Mean_DSPI'] = df.mean(axis=1)
    df = df.sort_values('Mean_DSPI', ascending=False)
    df.drop(columns=['Mean_DSPI'], inplace=True)

    plt.figure(figsize=(10, 8))
    
    # Create Heatmap
    # annot=True to show values
    # cmap="RdYlGn_r" -> Red is expensive (high), Green is cheap (low) - or reversed?
    # DSPI low (Cheap) = Green. DSPI High (Expensive) = Red.
    # So "RdYlGn" -> Red (Low) to Green (High). We want opposite. "RdYlGn" -> Red=0, Green=1. 
    # Usually Red=High Price is bad for consumer? Or Green=Cheap is good?
    # Arbitrageur perspective: Low is GOOD (Green). High is BAD (Red).
    # So Low (0.2) should be Green. High (1.2) should be Red.
    # "RdYlGn" maps Low->Red, High->Green.
    # So we need "RdYlGn_r".
    
    sns.heatmap(df, annot=True, cmap="RdYlGn_r", center=0.7, fmt=".2f", linewidths=.5, cbar_kws={'label': 'DSPI (1.0 = US Baseline)'})
    
    plt.title('Digital Services Price Index (DSPI) Heatmap\n(Lower Value = Higher Arbitrage Incentive)')
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, 'dspi_heatmap.pdf')
    plt.savefig(output_path)
    print(f"Saved heatmap to {output_path}")

if __name__ == "__main__":
    generate_dspi_heatmap()
