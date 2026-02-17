"""
Fix DSPI_Data.csv: Convert NordVPN (27mo), ExpressVPN (28mo), MS365 (12mo)
from total plan prices to monthly equivalents.

DSPI values remain unchanged (ratios cancel out).
Affected columns: Price_USD, US_Baseline_Price, Affordability_Wage_Based_%,
                  Real_Diff_USD
Unchanged columns: Original_Price, Currency, Exchange_Rate, DSPI,
                   Real_Diff_USD_%, Monthly_Salary_USD
"""

import csv
import sys

PLAN_MONTHS = {
    "NordVPN": 27,
    "ExpressVPN": 28,
    "Microsoft 365": 12,
}

INPUT = "SSoT_CSVs/DSPI_Data.csv"
OUTPUT = "SSoT_CSVs/DSPI_Data.csv"

def main():
    with open(INPUT, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print("=== BEFORE vs AFTER (affected rows) ===\n")
    print(f"{'Service':<18} {'Country':<18} {'Old Price_USD':>14} {'New Price_USD':>14} {'Old Baseline':>14} {'New Baseline':>14} {'Old Afford%':>12} {'New Afford%':>12} {'Old RealDiff':>12} {'New RealDiff':>12}")
    print("-" * 160)

    # First pass: compute new US baselines
    new_baselines = {}
    for row in rows:
        svc = row["Service"]
        if svc in PLAN_MONTHS and row["Country"] == "United States":
            months = PLAN_MONTHS[svc]
            old_baseline = float(row["US_Baseline_Price"])
            new_baselines[svc] = old_baseline / months

    for row in rows:
        svc = row["Service"]
        if svc not in PLAN_MONTHS:
            continue

        months = PLAN_MONTHS[svc]
        old_price = float(row["Price_USD"])
        old_baseline = float(row["US_Baseline_Price"])
        old_afford = float(row["Affordability_Wage_Based_%"])
        old_real_diff = float(row["Real_Diff_USD"])
        salary = float(row["Monthly_Salary_USD"])

        new_price = old_price / months
        new_baseline = old_baseline / months
        new_afford = new_price / salary
        new_real_diff = new_price - new_baseline

        print(f"{svc:<18} {row['Country']:<18} {old_price:>14.4f} {new_price:>14.4f} {old_baseline:>14.4f} {new_baseline:>14.4f} {old_afford:>12.6f} {new_afford:>12.6f} {old_real_diff:>12.4f} {new_real_diff:>12.4f}")

        row["Price_USD"] = f"{new_price}"
        row["US_Baseline_Price"] = f"{new_baseline}"
        row["Affordability_Wage_Based_%"] = f"{new_afford}"
        row["Real_Diff_USD"] = f"{new_real_diff}"

    # Write back
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote corrected data to {OUTPUT}")

    # === Generate LaTeX replacement values ===
    print("\n\n=== TABLE 6 (tab:dspi_usd) - Monthly USD prices ===\n")
    countries_order = ["Switzerland", "United Kingdom", "Germany", "United States",
                       "Poland", "Argentina", "Turkey", "Ukraine", "Brazil",
                       "Philippines", "Pakistan"]
    for country in countries_order:
        vals = {}
        for row in rows:
            if row["Country"] == country and row["Service"] in PLAN_MONTHS:
                vals[row["Service"]] = float(row["Price_USD"])
        ms = vals.get("Microsoft 365", 0)
        nord = vals.get("NordVPN", 0)
        expr = vals.get("ExpressVPN", 0)
        print(f"{country:<18} MS365=${ms:.2f}  NordVPN=${nord:.2f}  ExpressVPN=${expr:.2f}")

    print("\n\n=== TABLE 4 (tab:ptw_matrix) - PTW% values ===\n")
    for country in countries_order:
        vals = {}
        for row in rows:
            if row["Country"] == country and row["Service"] in PLAN_MONTHS:
                vals[row["Service"]] = float(row["Affordability_Wage_Based_%"]) * 100
        ms = vals.get("Microsoft 365", 0)
        nord = vals.get("NordVPN", 0)
        expr = vals.get("ExpressVPN", 0)
        print(f"{country:<18} MS365={ms:.2f}%  NordVPN={nord:.2f}%  ExpressVPN={expr:.2f}%")

    print("\n\n=== TABLE 3 (tab:app_dspi) - Average PTW% per country ===\n")
    for country in countries_order:
        country_rows = [r for r in rows if r["Country"] == country]
        ptw_vals = [float(r["Affordability_Wage_Based_%"]) * 100 for r in country_rows]
        n_services = len(ptw_vals)
        avg_ptw = sum(ptw_vals) / n_services if n_services > 0 else 0
        print(f"{country:<18} N={n_services}  Avg PTW = {avg_ptw:.2f}%")


if __name__ == "__main__":
    main()
