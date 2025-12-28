import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths
FIG_DIR = r"Latex Thesis\figures"
DATA_DIR = r"Quantitative DATA"

# Ensure output dir exists
os.makedirs(FIG_DIR, exist_ok=True)

def generate_dspi_heatmap():
    print("Generating DSPI Heatmap...")
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_DSPI.csv"))
    # Pivot: Index=Country, Columns=Service, Values=DSPI
    # Filter for heatmap-relevant services if needed or take all
    pivot = df.pivot_table(index='Country', columns='Service', values='DSPI')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, cmap="RdYlGn_r", annot=True, fmt=".2f", linewidths=.5)
    plt.title("Global Heatmap of Digital Service Pricing (DSPI)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "dspi_heatmap.pdf"))
    plt.close()

def generate_affordability_heatmap():
    print("Generating Affordability Heatmap...")
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_DSPI.csv"))
    # Metric: Affordability_Wage_Based_%
    pivot = df.pivot_table(index='Country', columns='Service', values='Affordability_Wage_Based_%')
    
    plt.figure(figsize=(12, 8))
    # Red is bad (high cost), Green is good (low cost)
    sns.heatmap(pivot, cmap="RdYlGn_r", annot=True, fmt=".2f", linewidths=.5)
    plt.title("Affordability: Cost as % of Median Monthly Wage")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "affordability_heatmap.pdf"))
    plt.close()

def generate_correlation_plot():
    print("Generating Correlation Scatter...")
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Correlation.csv"))
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Price_Discrimination_Score', y='Enforcement_Intensity_Percent', hue='Service', s=100)
    
    # Add labels
    for i, row in df.iterrows():
        plt.text(row['Price_Discrimination_Score']+0.01, row['Enforcement_Intensity_Percent'], 
                 row['Service'], fontsize=9)
                 
    plt.title("Price Discrimination vs Enforcement Intensity")
    plt.xlabel("Price Discrimination Score (StdDev DSPI)")
    plt.ylabel("Enforcement Intensity (%)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "protection_vs_pricing.pdf"))
    plt.close()

def generate_timeline_plot():
    print("Generating Timeline...")
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Qual_Timeline.csv"))
    df = df.set_index('Year')
    
    plt.figure(figsize=(12, 6))
    # Line chart for each column
    sns.lineplot(data=df, dashes=False, markers=True)
    plt.title("Evolution of Strategic Frames (2016-2024)")
    plt.ylabel("Frequency (%)")
    plt.xlabel("Year")
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "category_timeline_all_normalized.pdf"))
    plt.close()

def generate_distribution_pie():
    print("Generating Distribution Bar...")
    df = pd.read_csv(os.path.join(DATA_DIR, "Sheets_Import_Qual_Counts.csv"))
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, y='Category', x='Percent', orient='h')
    plt.title("Proportional Distribution of Enforcement Categories")
    plt.xlabel("Frequency (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "service_distribution_ratios.pdf"))
    plt.close()

if __name__ == "__main__":
    generate_dspi_heatmap()
    generate_affordability_heatmap()
    generate_correlation_plot()
    generate_timeline_plot()
    generate_distribution_pie()
    print("All figures regenerated in Latex Thesis/figures/")
