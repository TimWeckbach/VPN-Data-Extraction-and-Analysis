import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

captions = re.finditer(r'\\caption\{(.*?)\}', content, re.DOTALL)

with open('all_captions.txt', 'w', encoding='utf-8') as f_out:
    for i, match in enumerate(captions, 1):
        f_out.write(f"Caption {i}:\n{match.group(1)}\n")
        f_out.write("-" * 20 + "\n")
