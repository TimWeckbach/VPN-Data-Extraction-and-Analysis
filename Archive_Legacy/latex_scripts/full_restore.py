import re
import os

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

main_path = 'main.tex'
archive_path = r'archive\results_analysis.tex'

main_content = read_file(main_path)
archive_content = read_file(archive_path)

# 1. Identify Insertion Point (Line 719ish)
# Look for "% --- Generated Video Group ---"
# followed by the BAD block (Spotify in Video Group)
# We will replace the BAD block with ARCHIVE content.

# The bad block starts at "% --- Generated Video Group ---"
# And ends before "In the "Software and Music" category..." (Line 806)
start_marker = "% --- Generated Video Group ---"
end_marker_text = 'In the "Software and Music" category'

start_idx = main_content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker")
    exit(1)

end_idx = main_content.find(end_marker_text, start_idx)
if end_idx == -1:
    # Try finding the figure end
    print("Could not find end marker text, looking for end of bad figure")
    # Bad figure is fig:evol_software_main at 803
    end_marker_lbl = r'\label{fig:evol_software_main}'
    end_lbl_idx = main_content.find(end_marker_lbl, start_idx)
    if end_lbl_idx != -1:
        # Find \end{figure}
        end_fig_idx = main_content.find(r'\end{figure}', end_lbl_idx)
        if end_fig_idx != -1:
            end_idx = end_fig_idx + len(r'\end{figure}')
    
    if end_idx == -1:
        print("Could not determine end of block")
        exit(1)

print(f"Replacing block from {start_idx} to {end_idx}")

# Read archive content
# We want EVERYTHING from archive?
# Yes.
restored_content = archive_content

# Construct new content
new_main = main_content[:start_idx] + "\n" + restored_content + "\n" + main_content[end_idx:]

# 2. Cleanup Duplicates
# We now have:
# [Restored Archive Content] (contains individual plots)
# [Existing Individual Plots] (lines 1100-1400 in original, now shifted)
# [New Consolidated Plots] (lines 1500+)
# We want to remove INDIVIDUAL PLOTS from specific ranges.

# Regex to find individual plots:
# \label{fig:evol_netflix}, \label{fig:evol_youtube}, etc.
# We want to remove the FIGURE ENVIRONMENTS containing these labels.
targets = [
    r'fig:evol_netflix', r'fig:evol_youtube', r'fig:evol_disney',
    r'fig:evol_spotify', r'fig:evol_apple_music', r'fig:evol_microsoft', r'fig:evol_adobe',
    r'fig:evol_amazon'
]

# We need to be careful NOT to remove the Consolidated plots if they use these labels?
# New Consolidated plots use \label{fig:evol_video_main} and \label{fig:evol_software_main}.
# So safe to remove targets.

def remove_figure_by_label(content, label):
    # Pattern: \begin{figure} ... \label{label} ... \end{figure}
    # Note: re.DOTALL is needed.
    # We construct a regex that finds the figure environment containing the label.
    # Finds the label, then looks backwards for begin{figure} and forwards for end{figure}.
    # This is tricky with regex.
    # Better: iterating.
    
    # Simple regex approach:
    # \\begin\{figure\}\[ht\].*?\\label\{label\}.*?\\end\{figure\}
    # But this assumes structure.
    pattern = re.compile(r'\\begin\{figure\}.*?\\label\{' + label + r'\}.*?\\end\{figure\}', re.DOTALL)
    
    new_c, count = pattern.subn('', content)
    print(f"Removed {count} occurrences of {label}")
    return new_c

for t in targets:
    new_main = remove_figure_by_label(new_main, t)

# 3. Clean up the "Generated Video Group" marker if it was preserved/duplicated
new_main = new_main.replace("% --- Generated Video Group ---", "")

write_file('main_restored_full.tex', new_main)
print("Wrote main_restored_full.tex")

