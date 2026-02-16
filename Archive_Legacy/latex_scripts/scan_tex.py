import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all figures
figures = re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}', content, re.DOTALL)
tables = re.finditer(r'\\begin\{table\}.*?\\end\{table\}', content, re.DOTALL)
includes = re.finditer(r'\\include\{.*?\}|\\input\{.*?\}', content)
includegraphics = re.finditer(r'\\includegraphics.*?\{.*?\}', content)

with open('audit_report.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("--- FIGURES ---\n")
    for i, match in enumerate(figures, 1):
        caption_match = re.search(r'\\caption\{(.*?)\}', match.group(0), re.DOTALL)
        label_match = re.search(r'\\label\{(.*?)\}', match.group(0))
        tikz_check = "tikzpicture" in match.group(0) or "pgfplots" in match.group(0)
        img_check = "includegraphics" in match.group(0)
        
        caption = caption_match.group(1).replace('\n', ' ') if caption_match else "NO CAPTION"
        label = label_match.group(1) if label_match else "NO LABEL"
        
        f_out.write(f"Figure {i}:\n")
        f_out.write(f"  Caption: {caption[:100]}...\n")
        f_out.write(f"  Label: {label}\n")
        f_out.write(f"  Native LaTeX (TikZ/PGF): {tikz_check}\n")
        f_out.write(f"  Includes Image: {img_check}\n")
        f_out.write("-" * 20 + "\n")

    f_out.write("\n--- TABLES ---\n")
    for i, match in enumerate(tables, 1):
        caption_match = re.search(r'\\caption\{(.*?)\}', match.group(0), re.DOTALL)
        label_match = re.search(r'\\label\{(.*?)\}', match.group(0))
        
        caption = caption_match.group(1).replace('\n', ' ') if caption_match else "NO CAPTION"
        label = label_match.group(1) if label_match else "NO LABEL"
        
        f_out.write(f"Table {i}:\n")
        f_out.write(f"  Caption: {caption[:100]}...\n")
        f_out.write(f"  Label: {label}\n")
        f_out.write("-" * 20 + "\n")

    f_out.write("\n--- FIGURE REFERENCE CHECK ---\n")
    # Collect all figure labels
    fig_labels = []
    for match in figures:
        label_match = re.search(r'\\label\{(.*?)\}', match.group(0))
        if label_match:
            fig_labels.append(label_match.group(1))

    # Check if they are referenced
    for label in fig_labels:
        # Simple regex for \ref{label}, \autoref{label}, \cref{label}, etc.
        # We search the WHOLE content, but excluding the definition itself is hard with simple regex 
        # so we just count occurrences. If count > 1, it's likely referenced (1 for label, 1+ for ref).
        # Actually, \label{foo} is unique. any other occurrence of "foo" in a specific pattern is a ref.
        # Let's just search for the string label.
        count = content.count(label)
        # If count == 1, it's only defined, never referenced.
        if count <= 1:
             f_out.write(f"WARNING: Figure Label '{label}' appears only {count} time(s). Orphaned?\n")
        else:
             # f_out.write(f"OK: '{label}' referenced {count-1} times.\n") # Verbose
             pass
    
    if not any(content.count(l) <= 1 for l in fig_labels):
        f_out.write("All figure labels are referenced at least once.\n")

    f_out.write("\n--- EXTERNAL INCLUDES ---\n")
    for match in includes:
        start_pos = match.start()
        # Check backward to the beginning of the line
        line_start = content.rfind('\n', 0, start_pos) + 1
        line_content = content[line_start:start_pos]
        is_commented = '%' in line_content
        f_out.write(f"Include: {match.group(0)} (Commented: {is_commented})\n")

    f_out.write("\n--- STANDALONE IMAGES ---\n")
    for match in includegraphics:
        f_out.write(f"Image: {match.group(0)}\n")
