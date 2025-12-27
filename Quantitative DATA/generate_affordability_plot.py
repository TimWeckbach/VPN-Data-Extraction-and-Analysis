
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Paths
INPUT_CSV = r"Quantitative DATA\dspi_raw_data.csv"
OUTPUT_DIR = r"Latex Thesis\figures"

def generate_affordability_plot():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    df = pd.read_csv(INPUT_CSV)
    
    # Filter out rows with no Affordability data
    df = df.dropna(subset=['Affordability_%'])
    
    # Pivot for Heatmap
    # Index=Country, Columns=Service, Values=Affordability_%
    pivot_df = df.pivot(index='Country', columns='Service', values='Affordability_%')
    
    # Sort by average affordability (Expensive countries at top)
    pivot_df['Mean'] = pivot_df.mean(axis=1)
    pivot_df = pivot_df.sort_values('Mean', ascending=False)
    pivot_df.drop(columns=['Mean'], inplace=True)
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Use a diverging scale? Or purely sequential. 0.1% -> 2%.
    # 'RdYlGn_r' (Red = High %, Green = Low %) -> Expensive is Bad.
    sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="RdYlGn_r", linewidths=.5, cbar_kws={'label': 'Cost as % of Monthly Salary'})
    
    plt.title('Affordability Gap: Digital Services Cost Relative to Local Income (%)', fontsize=14, weight='bold')
    plt.ylabel('')
    plt.xlabel('')
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, 'affordability_heatmap.pdf')
    plt.savefig(output_path)
    print(f"Saved affordability heatmap to {output_path}")

if __name__ == "__main__":
    generate_affordability_plot()
