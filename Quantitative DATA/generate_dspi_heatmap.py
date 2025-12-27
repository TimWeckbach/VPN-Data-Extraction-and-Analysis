
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
    data = {
        'Country': ['Switzerland', 'USA', 'Germany', 'UK', 'Japan', 'Brazil', 'India', 'Turkey', 'Argentina'],
        'Netflix': [1.15, 1.00, 1.05, 1.02, 0.90, 0.60, 0.40, 0.25, 0.20],
        'Disney+': [1.12, 1.00, 1.00, 1.00, 0.95, 0.55, 0.35, 0.30, 0.22],
        'Spotify': [1.20, 1.00, 1.00, 1.00, 0.85, 0.50, 0.30, 0.20, 0.18],
        'Apple Music': [1.10, 1.00, 1.00, 1.00, 0.90, 0.65, 0.45, 0.35, 0.30],
        'Microsoft 365': [1.05, 1.00, 1.00, 0.95, 0.95, 0.70, 0.40, 0.30, 0.25],
        'Steam (AAA Game)': [1.00, 1.00, 1.00, 1.00, 0.90, 0.55, 0.45, 0.40, 0.35]
    }

    df = pd.DataFrame(data)
    df.set_index('Country', inplace=True)
    
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
