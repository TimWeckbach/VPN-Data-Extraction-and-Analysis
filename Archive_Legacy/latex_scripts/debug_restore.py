import re
import os

def read_file(path):
    print(f"Reading {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
            print(f"Read {len(c)} chars.")
            return c
    except Exception as e:
        print(f"Error reading {path}: {e}")
        exit(1)

def write_file(path, content):
    print(f"Writing {path} ({len(content)} chars)...")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

main_path = 'main.tex'
archive_path = os.path.join('archive', 'results_analysis.tex')

main_content = read_file(main_path)
archive_content = read_file(archive_path)

print(f"Archive Starts with: {archive_content[:50]}")

# Marker
start_marker = "% --- Generated Video Group ---"
start_idx = main_content.find(start_marker)

if start_idx == -1:
    print(f"Marker '{start_marker}' NOT found in main.tex")
    # Maybe clean main.tex has it differently?
    # I'll search for the Spotify plot which is definitely there.
    # "\title{Spotify}" before "\title{Apple}"
    pass
else:
    print(f"Marker found at {start_idx}")

# Refined block detection
# The corrupted block has Spotify (Software) inside Video Group section.
# We want to delete from start_marker to the next valid section or block.
# Ideally we replace it with Archive content.

end_marker_snippet = 'In the "Software and Music" category'
end_idx = main_content.find(end_marker_snippet, start_idx)

if end_idx == -1:
    print("End marker not found.")
    exit(1)
else:
    print(f"End marker found at {end_idx}")

# Replacement
new_content = main_content[:start_idx] + "\n% INSERTED ARCHIVE CONTENT START\n" + archive_content + "\n% INSERTED ARCHIVE CONTENT END\n" + main_content[end_idx:]

# Cleanup duplicates
targets = [
    r'fig:evol_netflix', r'fig:evol_youtube', r'fig:evol_disney',
    r'fig:evol_spotify', r'fig:evol_apple_music', r'fig:evol_microsoft', r'fig:evol_adobe',
    r'fig:evol_amazon'
]

# Note: removing these will remove them from the INSERTED archive content too if we are not careful.
# But we WANT to remove them if we have Consolidated figures covering them.
# The Consolidated figures (Lines 1500+) utilize DIFFERENT labels:
# fig:evol_video_main, fig:evol_software_main.
# So removing fig:evol_netflix etc is CORRECT.

def remove_figure_by_label(content, label):
    # Regex to capture \begin{figure} ... \label{label} ... \end{figure}
    # We use a greedy match for the content inside, but bounded by figure env.
    
    # Robust pattern:
    # \begin{figure} [^}]* (content) \label{label} (content) \end{figure}
    # This is hard.
    # Simpler: Split by \begin{figure}, check chunks for label.
    
    chunks = re.split(r'(\\begin\{figure\})', content)
    out_chunks = []
    skip_next = False
    
    removed_count = 0
    
    # chunks[0] is pre-text
    # chunks[1] is \begin{figure}
    # chunks[2] is content + next text... this split is not sufficient because \end{figure} is not delimiter.
    
    # Use re.sub with function?
    # Match the whole figure environment.
    # \\begin\{figure\}(?:(?!\\end\{figure\}).)*?\\label\{LABEL\}(?:(?!\\end\{figure\}).)*?\\end\{figure\}
    
    pattern_str = r'\\begin\{figure\}.*?\\label\{' + re.escape(label) + r'\}.*?\\end\{figure\}'
    pattern = re.compile(pattern_str, re.DOTALL)
    
    new_c, count = pattern.subn('', content)
    print(f"Removed {count} occurrences of {label}")
    return new_c

for t in targets:
    new_content = remove_figure_by_label(new_content, t)

write_file('main_fixed.tex', new_content)
