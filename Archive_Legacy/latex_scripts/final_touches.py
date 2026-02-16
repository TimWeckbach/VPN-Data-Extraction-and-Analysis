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

# --- GENERIC GENERATOR ---
def generate_scatter_plot(title, xlabel, ylabel, data_points, color='tudablue'):
    # data_points: list of (label, x, y)
    plot_code = r"""
\begin{figure}[ht]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            width=0.9\textwidth, height=8cm,
            xlabel={""" + xlabel + r"""},
            ylabel={""" + ylabel + r"""},
            grid=major,
            only marks,
            nodes near coords,
            point meta=explicit symbolic,
        ]
            \addplot[mark=*, mark options={fill=""" + color + r""", draw=black}, text opacity=1] coordinates {
"""
    for d in data_points:
        # (x, y) [label]
        plot_code += f"                ({d[1]},{d[2]}) [{d[0]}]\n"
    
    plot_code += r"""            };
        \end{axis}
    \end{tikzpicture}
    \caption{""" + title + r"""}
    \label{fig:generated_scatter}
\end{figure}
"""
    return plot_code

def generate_bar_chart(title, xlabel, ylabel, data_pairs, color='tudablue', sort=False):
    # Same as before
    if sort:
        data_pairs.sort(key=lambda x: x[1])
    symbolic_y = ",".join([d[0] for d in data_pairs])
    plot_code = r"""
\begin{figure}[ht]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            xbar,
            width=0.9\textwidth,
            height=8cm,
            xlabel={""" + ylabel + r"""},
            symbolic y coords={""" + symbolic_y + r"""},
            ytick=data,
            nodes near coords,
            nodes near coords align={horizontal},
            xmin=0,
            bar width=15pt,
            yticklabel style={font=\footnotesize},
        ]
            \addplot[fill=""" + color + r"""] coordinates {
"""
    for d in data_pairs:
        plot_code += f"                ({d[1]},{d[0]})\n"
    
    plot_code += r"""            };
        \end{axis}
    \end{tikzpicture}
    \caption{""" + title + r"""}
    \label{fig:generated_fortress}
\end{figure}
"""
    return plot_code


# --- FIX 1: Fortress Index (Insert if missing) ---
# Check if Fortress Image exists (previous search failed).
# Check if Figure 7 Code exists (maybe from apply_fixes if it worked?)
# If not, generate and insert after Table 7.

if r'\label{fig:generated_fortress}' not in content:
    print("Inserting Fortress Index Figure...")
    # Get Data from Table 7 (tab:fortress_index)
    fortress_pattern = re.compile(r'\\begin\{tabularx\}.*?\\label\{tab:fortress_index\}', re.DOTALL)
    match = fortress_pattern.search(content)
    fortress_data = []
    if match:
        tbl = match.group(0)
        rows = re.findall(r'([A-Za-z0-9\+\s]+)\s&\s[A-Za-z\s]+\s&\s([0-9\.]+)\s\\\\', tbl)
        for r in rows:
            fortress_data.append((r[0].strip(), float(r[1])))
    else:
         fortress_data = [('ExpressVPN', 55.56), ('NordVPN', 50.00), ('YouTube Premium', 34.34),
        ('Microsoft', 32.76), ('Apple Music', 12.50), ('Adobe', 5.71),
        ('Amazon Prime', 2.94), ('Disney+', 2.04), ('Netflix', 2.03), ('Spotify', 0.43)]
    
    fig7_code = generate_bar_chart(
        "The Fortress Index: Percentage of Enforcement Clauses per Service",
        "Service", "Fortress Score (%)",
        fortress_data,
        color='tudared',
        sort=True
    )
    
    # Insert after Table 7 \end{table}
    # Find table environment ending
    # Search for label tab:fortress_index first, then find next \end{table}
    lbl_idx = content.find(r'\label{tab:fortress_index}')
    if lbl_idx != -1:
        end_tbl = content.find(r'\end{table}', lbl_idx)
        if end_tbl != -1:
            ins_pos = end_tbl + len(r'\end{table}')
            content = content[:ins_pos] + "\n" + fig7_code + "\n" + content[ins_pos:]
    else:
        print("Could not find Table 7 to insert Figure 7 after.")


# --- FIX 2: Replace Priority Shift (frame_dist...) with Ref ---
if 'frame_dist_2020_2025.pdf' in content:
    print("Replacing Priority Shift image with Reference...")
    # Regex to replace FIGURE block
    pattern = re.compile(r'\\begin\{figure\}.*?frame_dist_2020_2025\.pdf.*?\\end\{figure\}', re.DOTALL)
    replacement = r"See Figure \ref{fig:dist_strategic} for the temporal evolution of strategic frames."
    content = pattern.sub(replacement, content)


# --- FIX 3: Figure 16 (Scatter Plot) ---
# Check for 'protection_vs_pricing' image
if 'protection_vs_pricing' in content:
    print("Rebuilding Scatter Plot (Fig 16)...")
    
    # Get Data from Table (tab:correlation_data)
    # Service & PD Score & Enforcement %
    # Microsoft & 0.208 & 0.87
    corr_pattern = re.compile(r'\\begin\{tabular\}.*?\\label\{tab:correlation_data\}', re.DOTALL)
    match = corr_pattern.search(content)
    scatter_data = []
    if match:
        tbl = match.group(0)
        rows = re.findall(r'([A-Za-z0-9\+\s]+)\s&\s([0-9\.]+)\s&\s([0-9\.]+)\s\\\\', tbl)
        for r in rows:
            name = r[0].strip()
            x = float(r[1]) # PD Score
            y = float(r[2]) # Enf Intensity
            scatter_data.append((name, x, y))
    else:
         # Fallback
         scatter_data = [('Microsoft', 0.208, 0.87), ('YouTube Premium', 0.464, 3.07)]
    
    fig16_code = generate_scatter_plot(
        "Strategic Alignment: Price Discrimination vs. Enforcement Intensity",
        "Price Discrimination Score (DSPI StdDev)",
        "Enforcement Intensity (%)",
        scatter_data,
        color='tudablue'
    )
    
    # Replace contents
    pattern = re.compile(r'\\begin\{figure\}.*?protection_vs_pricing.*?\\end\{figure\}', re.DOTALL)
    content = pattern.sub(fig16_code.replace('\\', '\\\\'), content)


# Review Text Update around Figure 16
# "The refined analysis ($N=10$)..."
# Just ensure it's there.

write_file(path, content)
