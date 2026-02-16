file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
target_index = 64293

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

line_num = content.count('\n', 0, target_index) + 1
print(f"Index {target_index} is at line {line_num}")
