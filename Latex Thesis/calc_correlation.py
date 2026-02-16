import numpy as np
from scipy import stats

# Pairs (PD Score, Enforcement Intensity %) from tab:correlation_data
# NOTE: Old version used Fortress Index values instead of EI — corrected 2025-02.
data = [
    (0.112, 8.33),  # ExpressVPN
    (0.231, 5.45),  # NordVPN
    (0.464, 3.07),  # YouTube
    (0.208, 0.87),  # Microsoft
    (0.446, 0.75),  # Apple Music
    (0.245, 0.13),  # Adobe
    (0.304, 0.24),  # Amazon
    (0.324, 0.18),  # Disney+
    (0.352, 0.17),  # Netflix
    (0.486, 0.03)   # Spotify
]

pd_scores = [x[0] for x in data]
intensities = [x[1] for x in data]

r_all, p_all = stats.pearsonr(pd_scores, intensities)
print(f"Pearson r (all N=10): {r_all:.4f} (p={p_all:.4f})")

# Excluding VPNs (first 2 entries)
r_nv, p_nv = stats.pearsonr(pd_scores[2:], intensities[2:])
print(f"Pearson r (excl. VPNs N=8): {r_nv:.4f} (p={p_nv:.4f})")
