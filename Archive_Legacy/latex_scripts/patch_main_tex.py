import re

# Read main.tex
with open('main.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Read new plots
with open('service_plots_new.tex', 'r', encoding='utf-8') as f:
    new_plots = f.read()

# Verify new plots content
if not new_plots.strip():
    print("Error: new plots file is empty")
    exit(1)

# Define regex to find the two figures
# Figure 1: Caption "Strategic Evolution: Streaming Leaders"
# \begin{figure}[ht] ... \label{fig:evol_content_main} \end{figure}
# Figure 2: Caption "Strategic Evolution: Ecosystem Leaders"
# \begin{figure}[ht] ... \label{fig:evol_software_main} \end{figure}

# We want to replace both of them with the content of new_plots.
# new_plots contains TWO figures.
# The original file has two figures separated by text?
# Let's check the text between them.
# Line 1516: "The "Content Providers" ... show distinct evolutionary paths..."
# Line 1593: "In the "Software and Music" category..."
# The user might want the text to remain or be updated?
# Text at 1516 refers to "Netflix, YouTube, Disney+, Amazon Prime". 
# Text at 1593 refers to "Microsoft... Adobe... Spotify... Apple Music".
# This matches my new grouping!
# Group 1 (Video) -> Netflix, YouTube, Disney+, Amazon.
# Group 2 (Software) -> Spotify, Apple, Microsoft, Adobe.
# So I can just replace the FIGURE blocks and keep the text!

# Find Figure 1 block
# It starts with \begin{figure}[ht] and ends with \end{figure} containing label fig:evol_content_main
pattern1 = re.compile(r'\\begin\{figure\}\[ht\].*?\\label\{fig:evol_content_main\}.*?\\end\{figure\}', re.DOTALL)
match1 = pattern1.search(content)

if not match1:
    print("Could not find Figure 1 (evol_content_main)")
    # Try searching by caption if label is different
    pattern1 = re.compile(r'\\begin\{figure\}\[ht\].*?Strategic Evolution: Streaming Leaders.*?\\end\{figure\}', re.DOTALL)
    match1 = pattern1.search(content)

if match1:
    print(f"Found Figure 1 at {match1.span()}")
    # Replace with FIRST part of new_plots (Video Group)
    # new_plots has "% --- Generated Video Group ---" ... "% --- Generated Software Group ---"
    parts = new_plots.split('% --- Generated Software Group ---')
    video_plot = parts[0].strip()
    software_plot = parts[1].strip() if len(parts) > 1 else ""
    
    content = content[:match1.start()] + video_plot + content[match1.end():]
else:
    print("Failed to replace Figure 1")

# Find Figure 2 block (adjust search text since content changed length? No, regex search on new content string is tricky)
# We should do replacements carefully.
# Because strings are immutable, I should have calculated positions first?
# Or just search again.

# Find Figure 2 block
# \label{fig:evol_software_main}
pattern2 = re.compile(r'\\begin\{figure\}\[ht\].*?\\label\{fig:evol_software_main\}.*?\\end\{figure\}', re.DOTALL)
match2 = pattern2.search(content)

if match2:
    print(f"Found Figure 2 at {match2.span()}")
    # Replace with software_plot
    # We need to use software_plot variable which we defined above.
    # But wait, we modified 'content' already. Indices might be invalid if we used match2 from OLD content.
    # We should search AGAIN in the NEW content.
    match2_new = pattern2.search(content)
    if match2_new:
        print(f"Found Figure 2 in new content at {match2_new.span()}")
        content = content[:match2_new.start()] + software_plot + content[match2_new.end():]
    else:
        print("Could not find Figure 2 in modified content")
else:
    print("Could not find Figure 2 in original content")

# Write back
with open('main.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully patched main.tex")
