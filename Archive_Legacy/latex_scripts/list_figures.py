import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if '\\begin{figure}' in line:
        print(f"L{i}: {line.strip()}")
        # Look ahead for caption
        for j in range(i, min(i+100, len(lines))):
            if '\\caption' in lines[j]:
                print(f"  Caption L{j+1}: {lines[j].strip()}")
                break
            if '\\label' in lines[j]:
                print(f"  Label L{j+1}: {lines[j].strip()}")
                break
