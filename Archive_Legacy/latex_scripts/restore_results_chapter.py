
import os

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

main_path = 'main.tex'
archive_path = os.path.join('archive', 'results_analysis.tex')

main_lines = read_file(main_path)
archive_lines = read_file(archive_path)

# Extract content from archive (Lines 1 to 247 - 0-indexed: 0 to 247)
# Line 248 in file is index 247.
# We want up to line 247 inclusive.
restore_content = archive_lines[:247] 

# Find insertion point in main.tex
# Looking for "The refined analysis ($N=10$)"
insert_idx = -1
for i, line in enumerate(main_lines):
    if "The refined analysis ($N=10$)" in line:
        insert_idx = i
        break

if insert_idx == -1:
    print("Error: Could not find insertion point 'The refined analysis ($N=10$)' in main.tex")
    # Fallback search? "The refined analysis"
    for i, line in enumerate(main_lines):
        if "The refined analysis" in line:
            insert_idx = i
            print(f"Found fallback insertion point at line {i+1}")
            break

if insert_idx != -1:
    # Prepare insertion block
    insertion = ["\n", "\\chapter{Results}\n", "\\label{chap:results}\n", "\n"] + restore_content + ["\n"]
    
    # Construct new content
    new_lines = main_lines[:insert_idx] + insertion + main_lines[insert_idx:]
    
    # Join and write
    new_content = "".join(new_lines)
    write_file(main_path, new_content)
    print(f"Successfully inserted {len(restore_content)} lines into main.tex at line {insert_idx+1}")
else:
    print("Could not find insertion point.")
