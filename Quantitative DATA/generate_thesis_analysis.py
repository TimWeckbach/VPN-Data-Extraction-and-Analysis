
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
    
    # 4. Timeline Graph (Changes over time)
    print("\n--- Timeline Analysis ---")
    # Group by Year and Category (Aggregated)
    time_group = df.groupby(['Year', target_col]).size().unstack(fill_value=0)
    
    # Plot 2: Line Chart over Time (All Services)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=time_group, dashes=False)
    plt.title('Category Frequency Over Time (All Services)')
    plt.ylabel('Frequency')
    plt.xlabel('Year')
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_timeline_all.pdf'))
    plt.close()

    # Plot 3: Faceted Timeline by Company
    # We need a long format for seaborn
    df_grouped = df.groupby(['Year', 'Company', target_col]).size().reset_index(name='Count')
    
    g = sns.FacetGrid(df_grouped, col="Company", col_wrap=3, height=4, sharey=False)
    g.map_dataframe(sns.lineplot, x="Year", y="Count", hue=target_col)
    g.add_legend()
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_timeline_per_service.pdf'))
    plt.close()
    
    print(f"\nGraphs saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_analysis()
