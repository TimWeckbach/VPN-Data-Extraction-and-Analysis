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

path = 'main.tex'
content = read_file(path)

# --- 1. REMOVE DUPLICATE SCATTER PLOT ---
# It has label fig:generated_scatter
pattern_dup = re.compile(r'\\begin\{figure\}.*?\\label\{fig:generated_scatter\}.*?\\end\{figure\}', re.DOTALL)
if pattern_dup.search(content):
    print("Removing duplicate scatter plot (fig:generated_scatter)...")
    content = pattern_dup.sub('', content)
else:
    print("Duplicate scatter plot not found.")

# --- 2. INSERT FORTRESS INDEX FIGURE ---
# Label in table is tab:fortress_index_complete
# We insert AFTER the table.

# Generate Code
fortress_data = [
    ('ExpressVPN', 55.56), ('NordVPN', 50.00), ('YouTube Premium', 34.34),
    ('Microsoft', 32.76), ('Apple Music', 12.50), ('Adobe', 5.71),
    ('Amazon Prime', 2.94), ('Disney+', 2.04), ('Netflix', 2.03), ('Spotify', 0.43)
]

# Sort for bar chart (descending usually looks best, but xbar with symbolic y needs correct order)
# xbar builds upward.
fortress_data.sort(key=lambda x: x[1]) # Ascending score = Ascending Y-axis (Top is highest score if we map index)
# Wait. Symbolic y coords: last element is top.
# So if we want Highest Score at Top, we need Ascending Order in list?
# Yes.
data_pairs = fortress_data
symbolic_y = ",".join([d[0] for d in data_pairs])

fig7_code = r"""
\begin{figure}[ht]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            xbar,
            width=0.9\textwidth,
            height=8cm,
            xlabel={Fortress Score (%)},
            symbolic y coords={""" + symbolic_y + r"""},
            ytick=data,
            nodes near coords,
            nodes near coords align={horizontal},
            xmin=0,
            bar width=15pt,
            yticklabel style={font=\footnotesize},
        ]
            \addplot[fill=tudared] coordinates {
"""
for d in data_pairs:
    fig7_code += f"                ({d[1]},{d[0]})\n"

fig7_code += r"""            };
        \end{axis}
    \end{tikzpicture}
    \caption{The Fortress Index: Percentage of Enforcement Clauses per Service}
    \label{fig:fortress_index}
\end{figure}
"""

if r'\label{fig:fortress_index}' not in content:
    print("Inserting Fortress Index Figure...")
    # Find table end
    lbl_idx = content.find(r'\label{tab:fortress_index_complete}')
    if lbl_idx != -1:
        end_tbl = content.find(r'\end{table}', lbl_idx)
        if end_tbl != -1:
            ins_pos = end_tbl + len(r'\end{table}')
            content = content[:ins_pos] + "\n" + fig7_code + "\n" + content[ins_pos:]
            print("Inserted Figure 7.")
        else:
            print("Could not find end of Table 7.")
    else:
        print("Could not find label tab:fortress_index_complete.")
else:
    print("fig:fortress_index already exists.")

write_file(path, content)
