file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
# Caption 12 (Fortress Index) Index: 69319
# Caption 10 (Keywords) Index: 64293
target_indices = {"Figure 7": 69319, "Table 3": 64293}

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

for name, idx in target_indices.items():
    line_num = content.count('\n', 0, idx) + 1
    print(f"{name} is around line {line_num}")
