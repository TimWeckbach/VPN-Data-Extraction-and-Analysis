file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
target_index = 45609

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

line_num = text.count('\n', 0, target_index) + 1
print(f"Caption 3 (Index 45609) is at line {line_num}")
