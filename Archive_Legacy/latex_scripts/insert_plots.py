import re

# Read main.tex
with open('main.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Read new plots
with open('service_plots_new.tex', 'r', encoding='utf-8') as f:
    new_plots = f.read()

# Find insertion point: after fig:timeline_service_latex (or fig:timeline)
# In Step 232: \label{fig:timeline} at line 1413.
# Pattern: \label{fig:timeline} ... \end{figure}
pattern = re.compile(r'\\label\{fig:timeline\}.*?\\end\{figure\}', re.DOTALL)
match = pattern.search(content)

if not match:
    # Try alternate label
    pattern = re.compile(r'\\label\{fig:timeline_service_latex\}.*?\\end\{figure\}', re.DOTALL)
    match = pattern.search(content)

if match:
    print(f"Found insertion point after {match.span()}")
    insertion_index = match.end()
    
    # Insert with some spacing
    new_content = content[:insertion_index] + "\n\n" + new_plots + "\n\n" + content[insertion_index:]
    
    with open('main.tex', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Inserted new plots.")
else:
    print("Could not find insertion point (fig:timeline).")
    # Backup strategy: Append to end of Chapter 6?
    # Or before "Detailed Analysis" (\label{sec:appendix_detailed_analysis} or similar)
    pass
