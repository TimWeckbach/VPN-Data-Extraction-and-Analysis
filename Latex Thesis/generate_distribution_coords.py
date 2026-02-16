import pandas as pd

CSV_PATH = 'Thesis_Dataset_Master_Redefined.csv'

# Colors from generate_service_evolution.py for consistency
colors = {
    'Content Licensing': 'blue',
    'Regulatory Compliance': 'orange',
    'Price Discrimination': 'green!60!black',
    'Legal Threat': 'red',
    'Technical Blocking': 'black',
    'Security Risk': 'brown',
    'Privacy/Security': 'brown!60!black',
    'Legitimate Portability': 'violet',
    'User Workaround': 'gray',
    'General Terms': 'gray!50',
    'Account Action': 'cyan', # Adding missing color if needed, check service evolution
    'IndividualError': 'pink'
}
# Service evolution used black for Account Action. Let's stick to that if possible, or distinct.
# Actually let's check service evolution colors again.
# 'Account Action': 'black' ?
# In previous script: 'Account Action' was not in the dict, so it got default black.
# 'Technical Blocking': 'black'.
# If both are black in stacked bar, we have a problem.
# I will set Account Action to 'cyan' or 'teal' to distinguish.
colors['Account Action'] = 'teal'
colors['Technical Blocking'] = 'black' 

# Read Data
df = pd.read_csv(CSV_PATH)
df = df[df['Year'] >= 2020]

def generate_dist_latex(df_subset, title_suffix, label_suffix):
    yearly_counts = df_subset.groupby(['Year', 'New_Category']).size().reset_index(name='Count')
    yearly_totals = df_subset.groupby('Year').size().reset_index(name='Total')
    merged = pd.merge(yearly_counts, yearly_totals, on='Year')
    merged['Share'] = (merged['Count'] / merged['Total']) * 100
    
    cats = merged['New_Category'].unique()
    
    print(f"% --- Distribution {title_suffix} ---")
    print(f"\\begin{{figure}}[ht]")
    print(f"    \\centering")
    print(f"    \\begin{{tikzpicture}}")
    print(f"        \\begin{{axis}}[")
    print(f"            ybar stacked,")
    print(f"            width=0.9\\textwidth,")
    print(f"            height=8cm,")
    print(f"            xlabel={{Year}},")
    print(f"            ylabel={{Share (\\%)}}")
    print(f"            xmin=2019.5, xmax=2025.5,")
    print(f"            ymin=0, ymax=100,")
    print(f"            xtick={{2020,2021,2022,2023,2024,2025}},")
    print(f"            xticklabel style={{/pgf/number format/set thousands separator={{}}}},")
    print(f"            legend style={{at={{(0.5,-0.2)}}, anchor=north, legend columns=3, font=\\footnotesize}},")
    print(f"            bar width=15pt,")
    print(f"            area style,") # Important for filling
    print(f"        ]")
    
    sorted_cats = sorted(cats)
    
    for cat in sorted_cats:
        cat_data = merged[merged['New_Category'] == cat].sort_values('Year')
        coords = []
        for y in range(2020, 2026):
            row = cat_data[cat_data['Year'] == y]
            if not row.empty:
                val = row['Share'].iloc[0]
            else:
                val = 0
            coords.append(f"({y},{val:.1f})")
        
        col = colors.get(cat, 'gray')
        
        # print(f"            \\addplot coordinates {{ {' '.join(coords)} }};")
        # Use fill options
        print(f"            \\addplot[ybar stacked, fill={col}, draw=black!50] coordinates {{ {' '.join(coords)} }};")
        print(f"            \\addlegendentry{{{cat}}}")
        
    print(f"        \\end{{axis}}")
    print(f"    \\end{{tikzpicture}}")
    print(f"    \\caption{{Distribution of Policy Text Categories Over Time ({title_suffix}).}}")
    print(f"    \\label{{fig:dist_{label_suffix}}}")
    print(f"\\end{{figure}}")
    print("\n")

# V1: Strategic Only
df_strat = df[df['New_Category'] != 'General Terms']
generate_dist_latex(df_strat, "Strategic Categories Only", "strategic")

# V2: All Categories
generate_dist_latex(df, "All Categories Including General", "all")
