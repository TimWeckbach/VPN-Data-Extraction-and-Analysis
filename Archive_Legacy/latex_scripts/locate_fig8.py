file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
# Caption 13 (Strategic Mix) Index: 72905
target_index = 72905

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

line_num = content.count('\n', 0, target_index) + 1
print(f"Figure 8 (Strategic Mix) is around line {line_num}")
