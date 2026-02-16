import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find all \begin and \end blocks and check their balance
def find_unbalanced(text):
    lines = text.split('\n')
    stack = []
    for i, line in enumerate(lines, 1):
        # Ignore comments
        line = line.split('%')[0]
        # Find all macros like \begin{foo} or \end{foo}
        matches = re.finditer(r'\\(begin|end)\{([a-zA-Z*]+)\}', line)
        for m in matches:
            kind = m.group(1)
            name = m.group(2)
            if kind == 'begin':
                stack.append((name, i))
            else:
                if not stack:
                    print(f"Error: \\end{{{name}}} at line {i} has no matching \\begin.")
                else:
                    last_name, last_line = stack.pop()
                    if last_name != name:
                        print(f"Error: \\end{{{name}}} at line {i} mismatches \\begin{{{last_name}}} at line {last_line}.")
    
    for name, line in stack:
        print(f"Error: \\begin{{{name}}} at line {line} is never closed.")

find_unbalanced(text)
