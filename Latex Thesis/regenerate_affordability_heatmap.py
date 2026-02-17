"""
Regenerate affordability_heatmap.pdf from the corrected DSPI_Data.csv (SSoT).
This replaces the old script that read from dspi_raw_data.csv (which had
Excel formulas and mismatched column names).
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

INPUT_CSV = "SSoT_CSVs/DSPI_Data.csv"
OUTPUT_DIR = "figures"

def main():
    df = pd.read_csv(INPUT_CSV)

    # Convert affordability from fraction to percentage
    df["Affordability_%"] = df["Affordability_Wage_Based_%"].astype(float) * 100

    # Pivot: rows=Country, columns=Service, values=Affordability_%
    pivot_df = df.pivot(index="Country", columns="Service", values="Affordability_%")

    # Sort by average affordability (most expensive countries at top)
    pivot_df["Mean"] = pivot_df.mean(axis=1)
    pivot_df = pivot_df.sort_values("Mean", ascending=False)
    pivot_df.drop(columns=["Mean"], inplace=True)

    # Reorder columns to match thesis order
    col_order = [
        "Netflix", "Youtube Premium", "Disney+", "Amazon Prime",
        "Spotify", "Apple Music", "Microsoft 365",
        "Adobe Creative Cloud", "Xbox Game Pass",
        "NordVPN", "ExpressVPN"
    ]
    col_order = [c for c in col_order if c in pivot_df.columns]
    pivot_df = pivot_df[col_order]

    # Plot
    plt.figure(figsize=(14, 8))
    sns.set_style("whitegrid")
    sns.heatmap(
        pivot_df, annot=True, fmt=".2f",
        cmap="RdYlGn_r", linewidths=0.5,
        cbar_kws={"label": "Cost as % of Monthly Salary"}
    )
    plt.title(
        "Affordability Gap: Digital Service Cost Relative to Local Income (%)",
        fontsize=14, weight="bold"
    )
    plt.ylabel("")
    plt.xlabel("")
    plt.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "affordability_heatmap.pdf")
    plt.savefig(output_path)
    print(f"Saved affordability heatmap to {output_path}")

    # Also print the data for verification
    print("\nAffordability data (% of monthly wage):")
    print(pivot_df.to_string())


if __name__ == "__main__":
    main()
