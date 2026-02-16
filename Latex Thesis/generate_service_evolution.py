import pandas as pd
import os

# Config
TARGET_COMPANIES = [
    'Adobe', 'Amazon', 'Apple Music', 'Disney+', 
    'Microsoft', 'Netflix', 'Spotify', 'Youtube Premium'
]
# Amazon Prime needs special handling for "Sentence Count" from Chart1
AMAZON_PRIME_CSV = 'SSoT_CSVs/Chart1_Terms_of_Service_Sentenc.csv'

CSV_PATH = 'Thesis_Dataset_Master_Redefined.csv'

# Read Master Data
df = pd.read_csv(CSV_PATH)
df = df[df['Year'] >= 2020]
df = df[df['New_Category'] != 'General Terms']

# Config Colors
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
    'Account Action': 'teal',
     'IndividualError': 'pink'
}
marks = {
    'Content Licensing': 'square*',
    'Regulatory Compliance': 'triangle*',
    'Price Discrimination': 'diamond*',
    'Legal Threat': 'pentagon*',
    'Technical Blocking': 'x',
    'Security Risk': 'asterisk',
    'Privacy/Security': 'otimes',
    'Legitimate Portability': 'oplus',
    'User Workaround': 'star',
    'General Terms': 'o',
    'Account Action': '*',
    'IndividualError': '*'
}

def generate_latex_plot(company_name, company_df, is_count=False):
    if is_count:
         # Special handling for Amazon Prime Chart1 data which is pivoted
         # Structure: Year, Cat1, Cat2...
         # We need to melt it
         melted = company_df.melt(id_vars=['Year'], var_name='New_Category', value_name='Count')
         melted = melted[melted['Count'] > 0] # Filter zeros
         merged = melted
         ylabel = "Sentence Count"
         title = f"{company_name} Sentence Count by Category"
         plot_type_options = "ybar stacked, bar width=15pt, area style,"
    else:
        # Standard Share calculation (Lines)
        yearly_counts = company_df.groupby(['Year', 'New_Category']).size().reset_index(name='Count')
        yearly_totals = company_df.groupby('Year').size().reset_index(name='Total')
        merged = pd.merge(yearly_counts, yearly_totals, on='Year')
        merged['Share'] = (merged['Count'] / merged['Total']) * 100
        ylabel = "Share (\\%)"
        title = f"{company_name} Category Evolution"
        plot_type_options = ""

    active_cats = merged['New_Category'].unique()
    
    print(f"% --- {company_name} ---")
    print(f"\\begin{{figure}}[ht]")
    print(f"    \\centering")
    print(f"    \\begin{{tikzpicture}}")
    print(f"        \\begin{{axis}}[")
    print(f"            {plot_type_options}")
    print(f"            width=0.8\\textwidth,")
    print(f"            height=6cm,")
    print(f"            xlabel={{Year}},")
    print(f"            ylabel={{{ylabel}}},")
    print(f"            xmin=2019.5, xmax=2025.5,")
    if not is_count:
        print(f"            ymin=0,")
    else:
        print(f"            ymin=0,")
    print(f"            xtick={{2020,2021,2022,2023,2024,2025}},")
    print(f"            xticklabel style={{/pgf/number format/set thousands separator={{}}}},")
    # print(f"            grid=major,") # Grid can look messy with bars, keep for lines or remove? Keep standard.
    print(f"            legend pos=outer north east,")
    print(f"            legend style={{font=\\tiny}},")
    print(f"            title={{{title}}},")
    print(f"            title style={{font=\\small\\bfseries}}")
    print(f"        ]")
    
    # Ensure stable sort for stacking
    active_cats = sorted(active_cats)

    for cat in active_cats:
        cat_data = merged[merged['New_Category'] == cat].sort_values('Year')
        coords = []
        for _, row in cat_data.iterrows():
            if is_count:
                 val = row['Count']
                 # Ensure we have data for all years in stack? 
                 # Matplotlib handles gaps, pgfplots usually skips.
                 # For stacked, it's safer to have 0s if year is missing?
                 # simplified here, assuming data exists.
            else:
                 val = row['Share']
            coords.append(f"({int(row['Year'])},{val:.1f})")
        
        col = colors.get(cat, 'black')
        mark = marks.get(cat, '*')
        
        if is_count:
            # Stacked Bar Style
            print(f"            \\addplot[ybar stacked, fill={col}, draw=black!50] coordinates {{ {' '.join(coords)} }};")
        else:
            # Line Style
            print(f"            \\addplot[thick, color={col}, mark={mark}] coordinates {{ {' '.join(coords)} }};")
        
        print(f"            \\addlegendentry{{{cat}}}")
        
    print(f"        \\end{{axis}}")
    print(f"    \\end{{tikzpicture}}")
    print(f"    \\caption{{{title} (2020--2025).}}")
    print(f"    \\label{{fig:evol_{company_name.lower().replace(' ', '_').replace('+', '')}}}")
    print(f"\\end{{figure}}")
    print("\n")

# 1. Generate Standard Plots
for company in TARGET_COMPANIES:
    c_df = df[df['Company'] == company]
    if not c_df.empty:
        generate_latex_plot(company, c_df)

# 2. Generate Amazon Prime Count Plot
if os.path.exists(AMAZON_PRIME_CSV):
    prime_df = pd.read_csv(AMAZON_PRIME_CSV, header=2)
    # Filter 2020+
    prime_df = prime_df[prime_df['Year'] >= 2020]
    # Filter General Terms (User Request)
    if 'General Terms' in prime_df.columns:
        prime_df = prime_df.drop(columns=['General Terms'])
    
    generate_latex_plot('Amazon Prime', prime_df, is_count=True)
