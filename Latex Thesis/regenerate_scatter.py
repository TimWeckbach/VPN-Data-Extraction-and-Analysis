"""
Regenerate Figure 7: PD Score vs Enforcement Intensity scatter plot.
Reads PD Scores from DSPI_Data.csv (SSoT) and enforcement data from
tab:correlation_data in main.tex.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats
from adjustText import adjust_text

# --- 1. Compute PD Scores (DSPI StdDev per service) from SSoT ---
csv_path = r'SSoT_CSVs\DSPI_Data.csv'
df = pd.read_csv(csv_path)

# Compute sample StdDev of DSPI per service
pd_scores = df.groupby('Service')['DSPI'].std().reset_index()
pd_scores.columns = ['Service', 'PD_Score']

# Service name mapping (CSV names -> short names used in thesis)
name_map = {
    'Netflix': 'Netflix',
    'Youtube Premium': 'YouTube Premium',
    'Disney+': 'Disney+',
    'Amazon Prime': 'Amazon Prime',
    'Spotify': 'Spotify',
    'Apple Music': 'Apple Music',
    'Microsoft 365': 'Microsoft',
    'Adobe Creative Cloud': 'Adobe',
    'Xbox Game Pass': 'Xbox GP',
    'NordVPN': 'NordVPN',
    'ExpressVPN': 'ExpressVPN',
}
pd_scores['Label'] = pd_scores['Service'].map(name_map)
pd_scores['PD_Score'] = pd_scores['PD_Score'].round(3)

print("=== Recalculated PD Scores from DSPI_Data.csv ===")
for _, row in pd_scores.sort_values('PD_Score', ascending=False).iterrows():
    print(f"  {row['Label']:20s}  PD = {row['PD_Score']:.3f}")

# --- 2. Enforcement Intensity data from tab:correlation_data ---
# These come from the ToS analysis, NOT from price data, so they're unchanged.
enforcement = {
    'Microsoft':      0.87,
    'YouTube Premium': 3.07,
    'Spotify':        0.03,
    'Adobe':          0.13,
    'Netflix':        0.17,
    'Disney+':        0.18,
    'Amazon Prime':   0.24,
    'Apple Music':    0.75,
    'ExpressVPN':     8.33,
    'NordVPN':        5.45,
}
# Xbox GP is excluded from correlation analysis (not in tab:correlation_data)

# --- 3. Merge ---
pd_scores['EI'] = pd_scores['Label'].map(enforcement)
plot_data = pd_scores.dropna(subset=['EI']).copy()

# Short labels for the plot
short_names = {
    'YouTube Premium': 'YouTube',
    'Amazon Prime': 'Amazon',
    'Apple Music': 'Apple Music',
}
plot_data['Short'] = plot_data['Label'].map(
    lambda x: short_names.get(x, x))

print("\n=== Data for scatter plot ===")
for _, row in plot_data.iterrows():
    print(f"  {row['Label']:20s}  PD={row['PD_Score']:.3f}  EI={row['EI']:.2f}%")

# --- 4. Compute correlations ---
x = plot_data['PD_Score'].values
y = plot_data['EI'].values

r_all, p_all = stats.pearsonr(x, y)
print(f"\nPearson r (all N={len(x)}): {r_all:.4f} (p={p_all:.4f})")

# Excluding VPNs
non_vpn = plot_data[~plot_data['Label'].isin(['NordVPN', 'ExpressVPN'])]
x_nv = non_vpn['PD_Score'].values
y_nv = non_vpn['EI'].values
r_nv, p_nv = stats.pearsonr(x_nv, y_nv)
print(f"Pearson r (excl. VPNs N={len(x_nv)}): {r_nv:.4f} (p={p_nv:.4f})")

# --- 5. Generate scatter plot ---
fig, ax = plt.subplots(figsize=(9, 6.5))

# Color coding by category
categories = {
    'Content':  ['Netflix', 'YouTube Premium', 'Disney+', 'Amazon Prime'],
    'Music':    ['Spotify', 'Apple Music'],
    'Software': ['Microsoft', 'Adobe'],
    'VPN':      ['NordVPN', 'ExpressVPN'],
}
cat_colors = {
    'Content':  '#004E8A',  # TUDa blue
    'Music':    '#009D81',  # TUDa green
    'Software': '#E98300',  # TUDa orange
    'VPN':      '#B90F22',  # TUDa red
}
cat_markers = {
    'Content':  'o',
    'Music':    's',
    'Software': 'D',
    'VPN':      '^',
}

for cat, services in categories.items():
    mask = plot_data['Label'].isin(services)
    subset = plot_data[mask]
    ax.scatter(subset['PD_Score'], subset['EI'],
               c=cat_colors[cat], marker=cat_markers[cat],
               s=110, label=cat, zorder=5, edgecolors='black', linewidth=0.5)

# --- Manual label placement based on adjustText output, no arrows ---
# Positions tuned from adjustText run, with Disney+ and Spotify nudged.
label_pos = {
    'ExpressVPN':      (0.015, 0.0),    # right of dot
    'NordVPN':         (0.015, 0.0),    # right of dot
    'YouTube':         (0.015, -0.15),  # right of dot
    'Apple Music':     (0.015, 0.0),    # right of dot
    'Microsoft':       (0.015, 0.25),   # above-right
    'Amazon':          (0.015, 0.35),   # above-right
    'Adobe':           (0.015, -0.35),  # below-right
    'Disney+':         (-0.005, -0.55), # below, shifted left
    'Netflix':         (0.015, 0.35),   # above-right
    'Spotify':         (-0.03, 0.15),   # above-left, closer to dot
}

for _, row in plot_data.iterrows():
    lbl = row['Short']
    dx, dy = label_pos.get(lbl, (0.015, 0.0))
    ax.annotate(lbl,
                xy=(row['PD_Score'], row['EI']),
                xytext=(row['PD_Score'] + dx, row['EI'] + dy),
                fontsize=8.5, ha='left', va='center', zorder=10)

ax.set_xlabel('Price Discrimination Score (DSPI Std. Dev.)', fontsize=11)
ax.set_ylabel('Enforcement Intensity (%)', fontsize=11)
ax.set_title('Strategic Alignment: Price Discrimination vs. Enforcement',
             fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.25, linestyle='--')
ax.set_xlim(0.04, 0.56)
ax.set_ylim(-0.5, 9.5)

# Add correlation annotation
ax.text(0.02, 0.97,
        f'Pearson r = {r_all:.3f} (p = {p_all:.2f})\n'
        f'Excl. VPNs: r = {r_nv:.3f} (p = {p_nv:.2f})',
        transform=ax.transAxes, fontsize=8.5, va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save as PDF
output_path = r'figures\protection_vs_pricing_updated.pdf'
with PdfPages(output_path) as pdf:
    pdf.savefig(fig, dpi=300)

print(f"\nFigure saved to: {output_path}")
plt.close()
