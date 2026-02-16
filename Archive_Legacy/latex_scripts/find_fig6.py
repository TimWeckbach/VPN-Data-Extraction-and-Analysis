import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "fig:global_priority_shift" in line:
        print(f"Found Figure 6 label at line {i}")
    if "Caption 9" in line: # Fallback
        print(f"Potential Figure 6 caption text at line {i}")
    if "\\label{fig:evol_software_main}" in line:
        print(f"Found Figure 13 at line {i}")
