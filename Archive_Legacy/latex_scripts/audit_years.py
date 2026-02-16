file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines, 1):
    if '2018' in line or '2019' in line:
        # Check if it's not part of a label or something legitimate (though user said "not in any figures or texts")
        # Just print everything for manual check
        print(f"L{i}: {line.strip()}")
        found = True

if not found:
    print("No 2018 or 2019 found.")
else:
    print("Please review the above lines.")
