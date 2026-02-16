"""
apply_forward_fill.py
=====================
Applies document-level forward-fill to the qualitative dataset.

Logic:
  - For each (Service, ToS-document-type), if a year within 2020-2025 has no
    new ToS publication, the most recent ToS is carried forward.
  - Non-ToS documents (10-K, Earnings, Shareholder Letters) are NOT forward-filled.
  - Uses Qual_Master.csv (curated categories) joined with the raw master CSV
    (to recover the Source column for document-level granularity).

Outputs (to SSoT_CSVs/):
  - Qual_Timeline.csv  (year x category aggregate -- overwrites old)
  - Service_Evolution.csv  (per-service year x category -- overwrites old)
"""

import pandas as pd
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
QUAL_MASTER = os.path.join(BASE, "SSoT_CSVs", "Qual_Master.csv")
RAW_MASTER = os.path.join(BASE, "Thesis_Dataset_Master_Redefined.csv")
SSOT_DIR = os.path.join(BASE, "SSoT_CSVs")

YEAR_MIN, YEAR_MAX = 2020, 2025

CATEGORIES = [
    "Technical Blocking", "Price Discrimination", "Content Licensing",
    "Regulatory Compliance", "Legal Threat", "Account Action",
    "Privacy/Security", "Security Risk", "Legitimate Portability",
    "User Workaround", "General Terms"
]

SERVICE_ORDER = [
    "Microsoft", "Youtube Premium", "Spotify", "Adobe", "Netflix",
    "Disney+", "Amazon Prime", "Apple Music", "ExpressVPN", "NordVPN"
]


def extract_tos_subtype(source_filename):
    """Extract ToS subtype from filename like '2023-12_Youtube_ToS_1_USA.pdf'."""
    if pd.isna(source_filename):
        return "unknown"
    m = re.search(r'_ToS(?:_(\d+))?_', str(source_filename))
    if m:
        return f"ToS_{m.group(1)}" if m.group(1) else "ToS"
    return "ToS"


def main():
    print("=" * 70)
    print("FORWARD-FILL ANALYSIS")
    print("=" * 70)

    # --- 1. Load data ---
    print("\n[1] Loading data...")
    qual = pd.read_csv(QUAL_MASTER)
    raw = pd.read_csv(RAW_MASTER)

    # Normalize column names
    if "Company" in raw.columns:
        raw.rename(columns={"Company": "Service"}, inplace=True)

    print(f"    Qual_Master: {len(qual)} rows")
    print(f"    Raw Master:  {len(raw)} rows")

    # --- 2. Join to recover Source column ---
    print("\n[2] Joining to recover Source column...")

    # Create a join key from sentence text (first 80 chars to handle truncation)
    qual["_join_key"] = qual["Sentence"].astype(str).str[:80]
    raw["_join_key"] = raw["Sentence"].astype(str).str[:80]

    # Build Source lookup from raw master (Year + Service + join_key -> Source)
    source_lookup = raw[["Year", "Service", "_join_key", "Source"]].drop_duplicates(
        subset=["Year", "Service", "_join_key"], keep="first"
    )

    qual_joined = qual.merge(
        source_lookup, on=["Year", "Service", "_join_key"], how="left"
    )
    matched = qual_joined["Source"].notna().sum()
    print(f"    Matched {matched}/{len(qual)} rows ({100*matched/len(qual):.1f}%)")

    # For unmatched ToS rows, assign a generic source
    tos_mask = qual_joined["Doc_Type"] == "Terms of Service"
    unmatched_tos = tos_mask & qual_joined["Source"].isna()
    if unmatched_tos.sum() > 0:
        print(f"    WARNING: {unmatched_tos.sum()} ToS rows without Source match")
        qual_joined.loc[unmatched_tos, "Source"] = (
            qual_joined.loc[unmatched_tos, "Year"].astype(str) + "_" +
            qual_joined.loc[unmatched_tos, "Service"] + "_ToS_USA"
        )

    qual_joined.drop(columns=["_join_key"], inplace=True)

    # --- 3. Determine ToS subtypes and forward-fill schedule ---
    print("\n[3] Building forward-fill schedule...")

    tos_data = qual_joined[qual_joined["Doc_Type"] == "Terms of Service"].copy()
    tos_data["ToS_Subtype"] = tos_data["Source"].apply(extract_tos_subtype)

    # For each (Service, ToS_Subtype), find publication years
    tos_years = tos_data.groupby(["Service", "ToS_Subtype"])["Year"].apply(
        lambda x: sorted(x.unique())
    ).reset_index()
    tos_years.columns = ["Service", "ToS_Subtype", "Pub_Years"]

    fill_plan = []
    for _, row in tos_years.iterrows():
        srv, subtype, pub_years = row["Service"], row["ToS_Subtype"], row["Pub_Years"]
        for i, pub_year in enumerate(pub_years):
            if pub_year < YEAR_MIN:
                next_year = pub_years[i + 1] if i + 1 < len(pub_years) else YEAR_MAX + 1
                for target in range(max(pub_year + 1, YEAR_MIN), min(next_year, YEAR_MAX + 1)):
                    fill_plan.append((srv, subtype, pub_year, target))
            elif pub_year <= YEAR_MAX:
                next_year = pub_years[i + 1] if i + 1 < len(pub_years) else YEAR_MAX + 1
                for target in range(pub_year + 1, min(next_year, YEAR_MAX + 1)):
                    fill_plan.append((srv, subtype, pub_year, target))

    print(f"    Forward-fill entries: {len(fill_plan)}")
    print(f"\n    {'Service':<18} {'ToS Type':<10} {'From':<6} {'To':<6} {'Rows':<6}")
    print("    " + "-" * 52)

    filled_rows = []
    total_added = 0
    for srv, subtype, src_year, tgt_year in fill_plan:
        mask = (
            (tos_data["Service"] == srv) &
            (tos_data["ToS_Subtype"] == subtype) &
            (tos_data["Year"] == src_year)
        )
        source_rows = tos_data[mask].copy()
        if len(source_rows) == 0:
            continue

        new_rows = source_rows.copy()
        new_rows["Year"] = tgt_year
        new_rows["Source"] = new_rows["Source"].astype(str) + f" [ffill->{tgt_year}]"
        filled_rows.append(new_rows)
        total_added += len(source_rows)
        print(f"    {srv:<18} {subtype:<10} {src_year:<6} {tgt_year:<6} {len(source_rows):<6}")

    print(f"\n    Total rows to add: {total_added}")

    # --- 4. Combine original + forward-filled data ---
    print(f"\n[4] Combining data...")
    if filled_rows:
        filled_df = pd.concat(filled_rows, ignore_index=True)
        combined = pd.concat([qual_joined, filled_df], ignore_index=True)
    else:
        combined = qual_joined
        filled_df = pd.DataFrame()

    timeline_data = combined[
        (combined["Year"] >= YEAR_MIN) & (combined["Year"] <= YEAR_MAX)
    ].copy()

    orig_count = len(qual_joined[(qual_joined["Year"] >= YEAR_MIN) & (qual_joined["Year"] <= YEAR_MAX)])
    print(f"    Original rows (2020-2025): {orig_count}")
    print(f"    Forward-filled rows added: {len(filled_df) if len(filled_df) > 0 else 0}")
    print(f"    Total rows (2020-2025):    {len(timeline_data)}")

    # --- 5. Generate Qual_Timeline ---
    print("\n[5] Generating Qual_Timeline.csv...")
    timeline_pivot = timeline_data.pivot_table(
        index="Year", columns="New_Category", values="Sentence",
        aggfunc="count", fill_value=0
    )
    cols = [c for c in CATEGORIES if c in timeline_pivot.columns]
    missing_cols = [c for c in CATEGORIES if c not in timeline_pivot.columns]
    for mc in missing_cols:
        timeline_pivot[mc] = 0
    cols = [c for c in CATEGORIES if c in timeline_pivot.columns]
    timeline_pivot = timeline_pivot[cols]

    # Include all years 2016-2025 for backward compat; fill pre-2020 from original
    orig_qual = pd.read_csv(os.path.join(SSOT_DIR, "Qual_Timeline.csv"))
    # Merge: keep pre-2020 from original, use filled for 2020-2025
    full_timeline = orig_qual.set_index("Year")
    for year in range(YEAR_MIN, YEAR_MAX + 1):
        if year in timeline_pivot.index:
            for c in cols:
                if c in full_timeline.columns:
                    full_timeline.loc[year, c] = int(timeline_pivot.loc[year, c])

    full_timeline.to_csv(os.path.join(SSOT_DIR, "Qual_Timeline.csv"))

    print("\n    QUAL TIMELINE (Forward-Filled, 2020-2025):")
    print(f"    {'Year':<6}", end="")
    short_names = {"Technical Blocking": "TechBl", "Price Discrimination": "PrDisc",
                   "Content Licensing": "CntLic", "Regulatory Compliance": "RegCom",
                   "Legal Threat": "LglThr", "Account Action": "AccAct",
                   "Privacy/Security": "Priv/S", "Security Risk": "SecRsk",
                   "Legitimate Portability": "LegPrt", "User Workaround": "UsrWrk",
                   "General Terms": "GenTrm"}
    for c in cols:
        print(f" {short_names.get(c, c[:6]):>7}", end="")
    print(f" {'TOTAL':>8}")

    for year in range(YEAR_MIN, YEAR_MAX + 1):
        if year in timeline_pivot.index:
            row = timeline_pivot.loc[year]
            total = int(row.sum())
            print(f"    {year:<6}", end="")
            for c in cols:
                print(f" {int(row.get(c, 0)):>7}", end="")
            print(f" {total:>8}")

    totals = timeline_pivot.loc[YEAR_MIN:YEAR_MAX].sum()
    grand_total = int(totals.sum())
    print(f"    {'TOTAL':<6}", end="")
    for c in cols:
        print(f" {int(totals.get(c, 0)):>7}", end="")
    print(f" {grand_total:>8}")

    # --- 6. Generate Service_Evolution ---
    print("\n[6] Generating Service_Evolution.csv...")
    lines_out = []
    for srv in SERVICE_ORDER:
        srv_data = timeline_data[timeline_data["Service"] == srv]
        srv_pivot = srv_data.pivot_table(
            index="Year", columns="New_Category", values="Sentence",
            aggfunc="count", fill_value=0
        )
        srv_pivot = srv_pivot.reindex(
            index=range(2016, YEAR_MAX + 1),
            columns=cols, fill_value=0
        )
        lines_out.append(f"{srv} Live Table")
        header = "Year," + ",".join(cols)
        lines_out.append(header)
        for year in range(2016, YEAR_MAX + 1):
            vals = [str(int(srv_pivot.loc[year].get(c, 0))) for c in cols]
            lines_out.append(f"{year},{','.join(vals)}")
        lines_out.append("")
        lines_out.append("")

    with open(os.path.join(SSOT_DIR, "Service_Evolution.csv"), "w", newline="") as f:
        f.write("\n".join(lines_out))

    # --- 7. Enforcement incidents ---
    print("\n[7] Enforcement incidents (Technical Blocking + Legal Threat):")
    coercive_cats = ["Technical Blocking", "Legal Threat"]
    coercive_data = timeline_data[timeline_data["New_Category"].isin(coercive_cats)]
    enforcement = coercive_data.pivot_table(
        index="Service", columns="Year", values="Sentence",
        aggfunc="count", fill_value=0
    )
    all_services = sorted(timeline_data["Service"].unique())
    enforcement = enforcement.reindex(
        index=all_services,
        columns=range(YEAR_MIN, YEAR_MAX + 1),
        fill_value=0
    )

    print(f"    {'Service':<18}", end="")
    for y in range(YEAR_MIN, YEAR_MAX + 1):
        print(f" {y:>6}", end="")
    print(f" {'Total':>7}")

    for srv in all_services:
        row = enforcement.loc[srv]
        total = int(row.sum())
        print(f"    {srv:<18}", end="")
        for y in range(YEAR_MIN, YEAR_MAX + 1):
            print(f" {int(row.get(y, 0)):>6}", end="")
        print(f" {total:>7}")

    total_row = enforcement.sum()
    gt = int(total_row.sum())
    print(f"    {'TOTAL':<18}", end="")
    for y in range(YEAR_MIN, YEAR_MAX + 1):
        print(f" {int(total_row.get(y, 0)):>6}", end="")
    print(f" {gt:>7}")

    # --- 8. Figure coordinates ---
    print("\n[8] Figure coordinates:")
    non_vpn = timeline_data[~timeline_data["Service"].isin(["ExpressVPN", "NordVPN"])]

    print("\n    --- fig:timeline_all (excl VPN) ---")
    for cat in ["Content Licensing", "Regulatory Compliance", "Technical Blocking",
                 "Price Discrimination", "Legal Threat", "Security Risk"]:
        cat_data = non_vpn[non_vpn["New_Category"] == cat]
        yearly = cat_data.groupby("Year").size()
        coords = " ".join(f"({y},{yearly.get(y,0)})" for y in range(YEAR_MIN, YEAR_MAX+1))
        print(f"    {cat:<25}: {coords}")

    print("\n    --- fig:strategic_frames_evolution (excl VPN+General) ---")
    other_cats = ["Privacy/Security", "Security Risk", "Legitimate Portability",
                  "User Workaround", "Account Action"]
    for cat in ["Content Licensing", "Regulatory Compliance", "Technical Blocking",
                 "Price Discrimination", "Legal Threat"]:
        cat_data = non_vpn[non_vpn["New_Category"] == cat]
        yearly = cat_data.groupby("Year").size()
        coords = " ".join(f"({y},{yearly.get(y,0)})" for y in range(YEAR_MIN, YEAR_MAX+1))
        print(f"    {cat:<25}: {coords}")
    other_data = non_vpn[non_vpn["New_Category"].isin(other_cats)]
    other_yearly = other_data.groupby("Year").size()
    coords = " ".join(f"({y},{other_yearly.get(y,0)})" for y in range(YEAR_MIN, YEAR_MAX+1))
    print(f"    {'Other (Priv,Sec,Port.)':<25}: {coords}")

    print("\n    --- fig:dist_strategic (all services, % shares) ---")
    strategic = timeline_data[timeline_data["New_Category"] != "General Terms"]
    yearly_total = strategic.groupby("Year").size()
    chart_cats = {
        "Content Licensing": ["Content Licensing"],
        "Regulatory Compliance": ["Regulatory Compliance"],
        "Technical Blocking": ["Technical Blocking"],
        "Price Discrimination": ["Price Discrimination"],
        "Enforcement Actions": ["Legal Threat", "Account Action", "Security Risk",
                                "Privacy/Security", "Legitimate Portability", "User Workaround"]
    }
    for label, cats in chart_cats.items():
        cat_data = strategic[strategic["New_Category"].isin(cats)]
        yearly_cat = cat_data.groupby("Year").size()
        pcts = []
        for y in range(YEAR_MIN, YEAR_MAX + 1):
            total = yearly_total.get(y, 1)
            count = yearly_cat.get(y, 0)
            pct = round(100 * count / total, 1) if total > 0 else 0.0
            pcts.append(f"({y},{pct})")
        print(f"    {label:<25}: {' '.join(pcts)}")

    print("\n" + "=" * 70)
    print("DONE.")
    print("=" * 70)


if __name__ == "__main__":
    main()
