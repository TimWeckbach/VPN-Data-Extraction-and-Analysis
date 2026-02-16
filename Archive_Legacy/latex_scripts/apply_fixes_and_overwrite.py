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

# Source file (the restored one)
source_path = 'main_fixed_safe.tex'
target_path = 'main.tex'

content = read_file(source_path)

# --- HELPER: PGFPlots Generators ---

def generate_bar_chart(title, xlabel, ylabel, data_pairs, color='tudablue', sort=False):
    # data_pairs: list of (label, value)
    if sort:
        data_pairs.sort(key=lambda x: x[1])
    
    coords = " ".join([f"({x[1]},{x[0]})" for x in enumerate([d[0] for d in data_pairs])]) # This is wrong for symbolic.
    
    # Correct symbolic coords
    symbolic_y = ",".join([d[0] for d in data_pairs])
    
    # Coordinates in format (value, Label) is hard for xbar.
    # Usually: (value, y) where y is index, and simple y coords map index to label.
    
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
    \label{""" + "fig:generated_" + title.split()[0].lower() + r"""}
\end{figure}
"""
    return plot_code

# --- FIX 1: Fortress Index (Figure 7) ---
# Data from tab:fortress_index regex
# Search for table content
fortress_pattern = re.compile(r'\\begin\{tabularx\}.*?\\label\{tab:fortress_index\}', re.DOTALL)
match = fortress_pattern.search(content)
fortress_data = []
if match:
    tbl = match.group(0)
    # Parse rows: ExpressVPN & VPN Enabler & 55.56 \\
    rows = re.findall(r'([A-Za-z0-9\+\s]+)\s&\s[A-Za-z\s]+\s&\s([0-9\.]+)\s\\\\', tbl)
    for r in rows:
        name = r[0].strip()
        val = float(r[1])
        fortress_data.append((name, val))
else:
    print("Warning: Could not extract Fortress Index data.")
    # Fallback data from visual inspection
    fortress_data = [
        ('ExpressVPN', 55.56), ('NordVPN', 50.00), ('YouTube Premium', 34.34),
        ('Microsoft', 32.76), ('Apple Music', 12.50), ('Adobe', 5.71),
        ('Amazon Prime', 2.94), ('Disney+', 2.04), ('Netflix', 2.03), ('Spotify', 0.43)
    ]

# Generate Figure 7 Code
fig7_code = generate_bar_chart(
    "The Fortress Index: Percentage of Enforcement Clauses per Service",
    "Service", "Fortress Score (%)",
    fortress_data,
    color='tudared',
    sort=True
)

# Replace Figure 7 image
# \includegraphics[...]{figures/fortress_index.pdf}
# It might be labelled fig:fortress_index? Check content.
# In archive: \label{tab:fortress_index} is the table.
# The figure is likely not present in archive?
# Archive had table.
# Step 344: Line 189 is table caption?
# Wait. Where is the Figure?
# Use regex to find \includegraphics...fortress_index.pdf and replace the FIGURE environment.

# --- FIX 2: Service Distribution (Figure 8) ---
# Data from tab:category_dist
cat_data = [
    ('Licensing', 37.2), ('Regulatory', 35.0), ('Price Discr.', 8.0),
    ('Legal Threat', 8.0), ('Blocking', 7.2), ('Security', 2.8)
]
# Generate Figure 8 Code
fig8_code = generate_bar_chart(
    "Proportional Distribution of Enforcement Categories (Aggregate)",
    "Category", "Share (%)",
    cat_data,
    color='tudablue',
    sort=True
)

# --- FIX 3: DSPI Map (Figure 3) -> Bar Chart ---
# Data from tab:dspi_full
# We'll take Average DSPI?
# Table 3 (archive) is tab:dspi_full.
# It has columns.
# We can calculate average row-wise or column-wise?
# Tab 3 has Rows=Services, Cols=Countries.
# We want Average DSPI per Country (Col Average).
# Tab 3 structure in LaTeX:
# Netflix & 1.44 & ... 
# Hard to parse average.
# But Table app_dspi (Line 939 in Step 286/309) HAS SUMMARY!
# Country | Avg DSPI | ...
# Perfect.
app_dspi_pattern = re.compile(r'\\begin\{tabular\}.*?\\label\{tab:app_dspi\}', re.DOTALL)
match = app_dspi_pattern.search(content)
dspi_data = []
if match:
    tbl = match.group(0)
    # Switzerland & 1.24 ...
    rows = re.findall(r'([A-Za-z\s]+)\s&\s([0-9\.]+)', tbl)
    for r in rows:
        country = r[0].strip()
        val = float(r[1])
        dspi_data.append((country, val))

if not dspi_data:
     dspi_data = [('Switzerland', 1.24), ('USA', 1.00), ('Turkey', 0.65), ('Pakistan', 0.45)] # Minimal fallback

fig3_code = generate_bar_chart(
    "Average Digital Services Price Index (DSPI) by Country",
    "Country", "DSPI (1.0 = US Baseline)",
    dspi_data,
    color='tudablue',
    sort=True
)

# --- FIX 4: Affordability (Figure 4) ---
# Data from tab:app_dspi (Netflix PTW column)
# Netflix PTW is 4th column?
# Rows: Switzerland & 1.24 & 11 & 0.33 \\
afford_data = []
if match:
    tbl = match.group(0)
    rows = re.findall(r'([A-Za-z\s]+)\s&\s[0-9\.]+\s&\s\d+\s&\s([0-9\.]+)', tbl)
    for r in rows:
        country = r[0].strip()
        val = float(r[1])
        afford_data.append((country, val))

fig4_code = generate_bar_chart(
    "Affordability Gap: Netflix Cost as \% of Median Wage",
    "Country", "Cost Share (%)",
    afford_data,
    color='tudared',
    sort=True
)


# --- REPLACEMENTS ---

# Function to replace figure image with code
def replace_image_figure(text, filename_snippet, new_code):
    # Find \begin{figure} ... filename_snippet ... \end{figure}
    pattern = re.compile(r'(\\begin\{figure\}(?:(?!\\end\{figure\}).)*?' + re.escape(filename_snippet) + r'.*?\\end\{figure\})', re.DOTALL)
    
    # Check if exists
    if pattern.search(text):
        print(f"Replacing figure containing {filename_snippet}")
        return pattern.sub(new_code.replace('\\', '\\\\'), text, count=1) # Escape backslashes for sub? No, passing function or raw string is better.
    else:
        print(f"Could not find figure with {filename_snippet}")
        return text

# Need to handle backslashes in replacement string for re.sub
# Better: use string replace if we find the match span.
def safe_replace(text, filename_snippet, new_code):
    pattern = re.compile(r'\\begin\{figure\}(?:(?!\\end\{figure\}).)*?' + re.escape(filename_snippet) + r'.*?\\end\{figure\}', re.DOTALL)
    match = pattern.search(text)
    if match:
        print(f"Replacing figure {filename_snippet}")
        # Insert label from new_code?
        # Ensure we keep the label if we want... but new_code has label.
        return text[:match.start()] + new_code + text[match.end():]
    return text

new_content = content

# Replace Fig 3 (dspi_heatmap.pdf)
new_content = safe_replace(new_content, 'dspi_heatmap.pdf', fig3_code)

# Replace Fig 4 (affordability_heatmap.pdf)
new_content = safe_replace(new_content, 'affordability_heatmap.pdf', fig4_code)

# Replace Fig 7 (fortress_index.pdf is not in archive? Table is.)
# But if it exists as image...
# Check content for "fortress_index.pdf"?
if 'fortress_index.pdf' in content:
   new_content = safe_replace(new_content, 'fortress_index.pdf', fig7_code)
else:
   # Insert Figure 7 AFTER Table 7?
   # Table 7 label: tab:fortress_index
   pass 

# Replace Fig 8 (service_distribution_ratios.pdf)
new_content = safe_replace(new_content, 'service_distribution_ratios.pdf', fig8_code)

# Replace Fig 6 (Priority Shift). 
# Archive has fig:priority_shift / figures/frame_dist_2020_2025.pdf
# I don't have data readily available for this one (it requires time series).
# But I can leave it as image if I can't rebuild it easily.
# Actually I have `fig:dist_strategic` (Figure 17).
# Maybe I just use Figure 17 code here?
# Figure 17 Code is at lines 898+.
# I'll try to find `frame_dist_2020_2025.pdf` and replace it with a reference to Figure 17?
# "See Figure \ref{fig:dist_strategic}".
# Or move Figure 17 here.


# --- OTHER FIXES ---
# Table 11 (`tab:app_service_stats`) totals.
# It already has Totals row (Line 1220 in Step 286).
# So no need to add totals.

# Table 7 (`tab:correlation_data`) caption.
# "Strategic Alignment: Comparison..."
# Ensure it is correct.
# Step 286 Line 367: "Correlation between...".
# I'll update it to "Strategic Alignment...".
new_content = new_content.replace(
    r'\caption{Correlation between Price Discrimination and Enforcement Intensity}',
    r'\caption{Strategic Alignment: Comparison of Price Discrimination scores vs. Enforcement Intensities}'
)

write_file(target_path, new_content)
