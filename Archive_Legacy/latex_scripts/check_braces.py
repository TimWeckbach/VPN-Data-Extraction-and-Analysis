import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern for \gls{...} and \glspl{...}
# We want to find ones that START but DON'T CLOSE correctly before the end of the line or before another macro.
# Actually, let's just count them.
def check_braces(text):
    errors = []
    # Find all instances of \gls{ or \glspl{
    for m in re.finditer(r'\\gls(pl)?\{', text):
        start = m.start()
        # Search for the closing brace
        depth = 1
        pos = m.end()
        found = False
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    found = True
                    break
            # If we hit a newline or a lot of space without a brace, it's likely an error in a caption
            if text[pos] == '\n' and depth > 0:
                # Potential error
                break
            pos += 1
        
        if not found:
            line_num = text.count('\n', 0, start) + 1
            snippet = text[start:start+40].replace('\n', ' ')
            errors.append(f"Line {line_num}: Unclosed brace starting at '{snippet}...'")
            
    return errors

errs = check_braces(text)
if not errs:
    print("No unclosed gls braces found.")
else:
    for e in errs:
        print(e)
