
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATA_FILE = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Dataset_Master_Redefined.csv"
OUTPUT_DIR = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\figures"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_analysis():
    print("Loading data...")
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # 1. Clean Data (Filter out empty categories if necessary, or count them)
    # Assuming 'New_Category' is the column for the finalized category or 'Label' from original
    # The user mentioned "Gemini vs BERT", we might have 'Category' or similar. 
    # Let's inspect columns first. Based on previous `head`, we have: Year, Company, Doc_Type, Sentence, Label, Score, Source, New_Category, Confidence
    
    target_col = 'New_Category' # Use this for final frequency 
    
    # 2. Exact Frequencies for LaTeX Table
    print("\n--- Exact Frequencies (Total) ---")
    freq_table = df[target_col].value_counts().reset_index()
    freq_table.columns = ['Category', 'Frequency']
    print(freq_table)

    # Generate LaTeX Table Content
    print("\n--- LaTeX Table Rows ---")
    for index, row in freq_table.iterrows():
        print(f"{row['Category']} & Description Placeholder & {row['Frequency']} \\\\")
        print("\\hline")

    # 3. Analysis per Service (Company)
    print("\n--- Analysis per Service ---")
    # Group by Company and Category
    service_group = df.groupby(['Company', target_col]).size().unstack(fill_value=0)
    print(service_group)
    
    # Ratios (Normalized)
    service_ratios = service_group.div(service_group.sum(axis=1), axis=0)
    
    # Plot 1: Stacked Bar Chart per Service
    plt.figure(figsize=(10, 6))
    service_ratios.plot(kind='bar', stacked=True, colormap='viridis', figsize=(12, 6))
    plt.title('Category Distribution by Service')
    plt.ylabel('Proportion')
    plt.xlabel('Service')
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'service_distribution_ratios.pdf'))
    plt.close()
    
    # 4. Timeline Graph (Changes over time) - NORMALIZED & FILTERED
    print("\n--- Timeline Analysis (Normalized) ---")
    
    # Calculate Total Sentences per Year
    yearly_totals = df.groupby('Year').size()
    
    # Group by Year and Category
    time_group = df.groupby(['Year', target_col]).size().unstack(fill_value=0)
    
    # Normalize: Divide each row by the yearly total
    time_norm = time_group.div(yearly_totals, axis=0) * 100 # In percentage
    
    # Filter out "General Terms" for the trend graph to see the signals
    if 'General Terms' in time_norm.columns:
        time_norm_filtered = time_norm.drop(columns=['General Terms'])
    else:
        time_norm_filtered = time_norm

    # Plot 2: Line Chart over Time (All Services) - Normalized & Filtered
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=time_norm_filtered, dashes=False)
    plt.title('Relative Frequency of Enforcement Categories Over Time (Excluding General Terms)')
    plt.ylabel('Percentage of Year\'s Sentences')
    plt.xlabel('Year')
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_timeline_all_normalized.pdf'))
    plt.close()

    # Plot 3: Faceted Timeline by Company - Normalized
    # We need a long format for seaborn, but calculated as percentage of THAT company's year total
    
    # helper to normalize within groups
    def normalize_year_company(x):
        return x / x.sum() * 100

    # Group by [Year, Company, Category], Count
    df_counts = df.groupby(['Year', 'Company', target_col]).size().reset_index(name='Count')
    
    # Calculate totals per [Year, Company]
    df_totals = df_counts.groupby(['Year', 'Company'])['Count'].transform('sum')
    
    # Calculate Percentage
    df_counts['Percentage'] = (df_counts['Count'] / df_totals) * 100
    
    # Filter "General Terms" for the faceted plot too
    df_counts_filtered = df_counts[df_counts[target_col] != 'General Terms']

    g = sns.FacetGrid(df_counts_filtered, col="Company", col_wrap=3, height=4, sharey=False)
    g.map_dataframe(sns.lineplot, x="Year", y="Percentage", hue=target_col)
    g.add_legend()
    g.set_axis_labels("Year", "Percentage of Sentences")
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_timeline_per_service_normalized.pdf'))
    plt.close()
    
    print(f"\nGraphs saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_analysis()
