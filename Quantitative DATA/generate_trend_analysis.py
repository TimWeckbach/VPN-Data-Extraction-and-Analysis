import pandas as pd
import os

def analyze_time_trend():
    base_path = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA"
    csv_file = os.path.join(base_path, "Thesis_Dataset_Master.csv")
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    print("LOADING DATA...")
    df = pd.read_csv(csv_file)
    
    # Clean Year column (handle occasional nans or weird types)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    # Filter for relevant years (2016-2025) to remove outliers if any
    df = df[df['Year'] >= 2016]

    # --- 1. Global Trend ---
    print(f"\n{'='*40}")
    print(f"GLOBAL COERCION TREND (All Companies)")
    print(f"{'='*40}")
    
    # Crosstab Year vs Label
    global_trend = pd.crosstab(df['Year'], df['Label'], normalize='index').mul(100).round(1)
    
    if 'coercive restriction and legal threat' in global_trend.columns:
        print(global_trend[['coercive restriction and legal threat']])
    
    # --- 2. Company Specific Trends ---
    print(f"\n{'='*40}")
    print(f"COERCION TREND BY COMPANY")
    print(f"{'='*40}")
    
    # Filter only Coercive rows to count them, then normalize by total rows per company-year
    # Pivot: Index=Year, Columns=Company, Values=Coercion%
    
    # First, calculate 'Coercive' count per Company/Year
    df['IsCoercive'] = df['Label'] == 'coercive restriction and legal threat'
    
    trend_pivot = df.pivot_table(
        index='Year', 
        columns='Company', 
        values='IsCoercive', 
        aggfunc='mean'
    ).mul(100).round(1)
    
    # Print the table filling NaNs with "-" for readability
    print(trend_pivot.fillna("-"))
    
    # Save to CSV
    output_dir = os.path.join(base_path, "_OUTPUTS")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "Analysis_Trend_Over_Time.csv")
    trend_pivot.to_csv(output_path)
    print(f"\n✅ Trend data saved to: {os.path.basename(output_path)}")

if __name__ == "__main__":
    analyze_time_trend()
