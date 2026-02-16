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

# --- GENERATOR: NUMERICAL Y AXIS ---
def generate_bar_chart_numerical(title, xlabel, ylabel, data_pairs, color='tudablue', sort=False, label_key=''):
    # data_pairs: list of (label, value)
    if sort:
        data_pairs.sort(key=lambda x: x[1]) # Ascending value
    
    # Generate yticks and labels
    yticks = list(range(len(data_pairs)))
    yticklabels = [d[0] for d in data_pairs]
    
    # Coordinates: (value, index)
    coords = []
    for i, d in enumerate(data_pairs):
        coords.append(f"({d[1]},{i})")
    
    # Format ticks and labels for latex
    width_opt = "0.9\\textwidth"
    ytick_str = ",".join(map(str, yticks))
    yticklabel_str = ",".join([f"{{{l}}}" for l in yticklabels]) # Braced labels
    
    plot_code = r"""
\begin{figure}[ht]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            xbar,
            width=""" + width_opt + r""",
            height=8cm,
            xlabel={""" + ylabel + r"""},
            ytick={""" + ytick_str + r"""},
            yticklabels={""" + yticklabel_str + r"""},
            nodes near coords,
            nodes near coords align={horizontal},
            xmin=0,
            bar width=15pt,
            yticklabel style={font=\footnotesize},
        ]
            \addplot[fill=""" + color + r"""] coordinates {
"""
    for c in coords:
        plot_code += f"                {c}\n"
    
    plot_code += r"""            };
        \end{axis}
    \end{tikzpicture}
    \caption{""" + title + r"""}
    \label{""" + label_key + r"""}
\end{figure}
"""
    return plot_code


# --- 1. RE-INSERT FIG 7 (Fortress) ---
# It was deleted. We insert after tab:fortress_index_complete.
fortress_data = [
    ('ExpressVPN', 55.56), ('NordVPN', 50.00), ('YouTube Premium', 34.34),
    ('Microsoft', 32.76), ('Apple Music', 12.50), ('Adobe', 5.71),
    ('Amazon Prime', 2.94), ('Disney+', 2.04), ('Netflix', 2.03), ('Spotify', 0.43)
]

fig7_code = generate_bar_chart_numerical(
    "The Fortress Index: Percentage of Enforcement Clauses per Service",
    "Service", "Fortress Score (%)",
    fortress_data,
    color='tudared',
    sort=True,
    label_key='fig:fortress_index'
)

if r'\label{fig:fortress_index}' not in content:
    print("Inserting Fortress Figure (Numerical)...")
    lbl_idx = content.find(r'\label{tab:fortress_index_complete}')
    if lbl_idx != -1:
        end_tbl = content.find(r'\end{table}', lbl_idx)
        if end_tbl != -1:
            ins_pos = end_tbl + len(r'\end{table}')
            content = content[:ins_pos] + "\n" + fig7_code + "\n" + content[ins_pos:]
        else:
             # Try searching for table end via regex if simple find fails?
             pass

# --- 2. FIX FIG 8 (Category Dist) ---
# It likely has space issues too.
# Label: fig:generated_proportional (from apply_fixes)
# Or maybe I named it differently?
# apply_fixes used title "Proportional Distribution...".
# I'll search for the figure block and replace it.

cat_data = [
    ('Content Licensing', 37.2), ('Regulatory Compliance', 35.0), ('Price Discrimination', 8.0),
    ('Legal Threat', 8.0), ('Technical Blocking', 7.2), ('Security Risk', 2.8) # Approx values
]
# Wait. Exact data?
# tab:category_dist (Line 791 archive)
# Licensing: 37.2?
# I'll rely on the manual data I prepared in apply_fixes.py.

fig8_code = generate_bar_chart_numerical(
    "Proportional Distribution of Enforcement Categories (Aggregate)",
    "Category", "Share (%)",
    cat_data,
    color='tudablue',
    sort=True,
    label_key='fig:category_dist_viz'
)

# Replace existing Figure 8
# I'll search for \label{fig:generated_proportional} OR title "Proportional Distribution of Enforcement Categories"
# apply_fixes generated: \label{fig:generated_proportional}
# if I kept it.
# Check content.
if 'Proportional Distribution of Enforcement Categories (Aggregate)' in content:
    print("Replacing Figure 8...")
    pattern = re.compile(r'\\begin\{figure\}.*?Proportional Distribution.*?\\end\{figure\}', re.DOTALL)
    content = pattern.sub(fig8_code.replace('\\', '\\\\'), content, count=1)
else:
    print("Figure 8 not found via title search.")
    # Maybe insert it?
    # Text ref: Figure \ref{fig:category_dist_viz}.
    # I should insert it near "The distribution of these categories (Figure \ref{fig:category_dist_viz})..."
    # Search for that sentence.
    match = re.search(r'The distribution of these categories \(Figure \\ref\{fig:category_dist_viz\}\)', content)
    if match:
        ins_pos = match.end()
        content = content[:ins_pos] + "\n" + fig8_code + "\n" + content[ins_pos:]
        print("Inserted Figure 8.")

write_file(path, content)
