import re
import os

def read_file(path):
    print(f"Reading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    print(f"Writing {path} ({len(content)} chars)...")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

main_path = 'main.tex'
archive_path = os.path.join('archive', 'results_analysis.tex')

main_content = read_file(main_path)
archive_content = read_file(archive_path)

# Marker
start_marker = "% --- Generated Video Group ---"
start_idx = main_content.find(start_marker)
end_marker_text = 'In the "Software and Music" category'
end_idx = main_content.find(end_marker_text, start_idx)

if start_idx == -1 or end_idx == -1:
    print("Markers not found!")
    exit(1)

# Replacement
# Insert Archive content in place of the corrupted block
new_content = main_content[:start_idx] + "\n% INSERTED ARCHIVE CONTENT START\n" + archive_content + "\n% INSERTED ARCHIVE CONTENT END\n" + main_content[end_idx:]

# Cleanup duplicates
targets = [
    r'fig:evol_netflix', r'fig:evol_youtube', r'fig:evol_disney',
    r'fig:evol_spotify', r'fig:evol_apple_music', r'fig:evol_microsoft', r'fig:evol_adobe',
    r'fig:evol_amazon'
]

def remove_figures(content, labels_to_remove):
    # Find all figure blocks
    # We use a pattern that matches \begin{figure} ... \end{figure}
    # We assume no nested figures.
    pattern = re.compile(r'(\\begin\{figure\}.*?\\end\{figure\})', re.DOTALL)
    
    parts = []
    last_pos = 0
    
    for match in pattern.finditer(content):
        block = match.group(1)
        start, end = match.span()
        
        # Append text before this block
        parts.append(content[last_pos:start])
        
        # Check if block contains any target label
        should_remove = False
        for lbl in labels_to_remove:
            if lbl in block:
                should_remove = True
                print(f"Removing figure with label {lbl}")
                break
        
        if not should_remove:
            parts.append(block)
        
        last_pos = end
    
    parts.append(content[last_pos:])
    return "".join(parts)

final_content = remove_figures(new_content, targets)

write_file('main_fixed_safe.tex', final_content)
