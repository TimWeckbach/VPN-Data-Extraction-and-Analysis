import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
# Regex for \gls{something and \glspl{something
# It handles alphanumeric and underscores inside the braces.
gls_pattern = re.compile(r'(\\gls(?:pl)?\{[a-zA-Z0-9_]+)')

for line_num, line in enumerate(lines, 1):
    # Find all occurrences of \gls{tag or \glspl{tag
    matches = list(gls_pattern.finditer(line))
    if matches:
        # Process backwards to not mess up indices
        for match in reversed(matches):
            start = match.start()
            end = match.end()
            # Check if there's a closing brace after the matched part
            # We look at the character exactly at 'end'
            if end >= len(line) or line[end] != '}':
                # Missing brace!
                line = line[:end] + '}' + line[end:]
                print(f"Fixed missing brace at L{line_num}: {line.strip()}")
    
    # Also clean up double braces like \gls{tag}} or \gls{tag}}}
    line = re.sub(r'(\\gls(?:pl)?\{[a-zA-Z0-9_]+\})\}+', r'\1', line)
    
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Unified Glossary Commands.")
