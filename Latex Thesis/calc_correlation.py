import numpy as np

# Pairs (PD Score, Enforcement Intensity) from CSV/Figure
# pd_scores = [0.112, 0.231, 0.464, 0.208, 0.446, 0.245, 0.304, 0.324, 0.352, 0.486]
# intensities = [55.56, 50.00, 34.34, 32.76, 12.50, 5.71, 2.94, 2.04, 2.03, 0.43]

data = [
    (0.112, 55.56), # ExpressVPN
    (0.231, 50.00), # NordVPN
    (0.464, 34.34), # YouTube
    (0.208, 32.76), # Microsoft
    (0.446, 12.50), # Apple Music
    (0.245, 5.71),  # Adobe
    (0.304, 2.94),  # Amazon
    (0.324, 2.04),  # Disney+
    (0.352, 2.03),  # Netflix
    (0.486, 0.43)   # Spotify
]

pd_scores = [x[0] for x in data]
intensities = [x[1] for x in data]

correlation = np.corrcoef(pd_scores, intensities)[0, 1]
print(f"Pearson Correlation Coefficient (r): {correlation:.4f}")
