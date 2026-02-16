import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines, 1):
    cleaned = line.split('%')[0]
    begins = re.findall(r'\\begin\{([a-zA-Z*]+)\}', cleaned)
    ends = re.findall(r'\\end\{([a-zA-Z*]+)\}', cleaned)
    
    for b in begins:
        stack.append((b, i))
    for e in ends:
        if stack and stack[-1][0] == e:
            stack.pop()
        else:
            print(f"Mismatch: Found \\end{{{e}}} at line {i} but expected \\end{{{stack[-1][0] if stack else 'NONE'}}}")

print("-" * 20)
for env, ln in stack:
    print(f"Unclosed: \\begin{{{env}}} at line {ln}")
