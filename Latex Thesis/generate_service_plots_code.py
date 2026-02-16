import pandas as pd
import io

csv_path = r'c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\tables\Digital Services Price Index (DSPI) - Service_Evolution.csv'

# Read entire file
with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

data_frames = []
current_service = None
current_data = []
header = None

for line in lines:
    line = line.strip()
    if 'Live Table' in line:
        # Start of new service block
        # e.g. "Microsoft Live Table,,,,,,,,,"
        current_service = line.split(' Live Table')[0]
        current_data = [] # Reset data
        header = None # Reset header
        # Check if previous block needs processing? No, we process line by line
    elif line.startswith('Year,'):
        # Header row
        header = line.split(',')
    elif line and current_service and header:
        # Data row
        # Parse based on header
        parts = line.split(',')
        if len(parts) >= len(header): # Ensure valid row
             # Create a dict for this row
             row_dict = {'Service': current_service}
             for i, col in enumerate(header):
                 if col and i < len(parts):
                     row_dict[col] = parts[i]
             current_data.append(row_dict)
             
             # If next line is empty or new table, we could process.
             # But easier: just append to a global list
             
# Wait, this loop structure is tricky for "end of block". 
# Better: Collect all rows then create DF.

# Revised logic:
all_rows = []
current_service = None
header = None

for line in lines:
    line = line.strip()
    if not line: continue
    
    if 'Live Table' in line:
        current_service = line.split(' Live Table')[0].strip()
        header = None
    elif line.startswith('Year,'):
        header = [c.strip() for c in line.split(',')]
    elif current_service and header:
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 2 and parts[0].isdigit(): # Check if Year is digit
            row = {'Service': current_service}
            for i, h in enumerate(header):
                if h and i < len(parts):
                    try:
                        row[h] = float(parts[i]) if parts[i] else 0.0
                    except ValueError:
                        row[h] = 0.0
            all_rows.append(row)

df = pd.DataFrame(all_rows)

# Melt to Long format
# Service, Year, Category, Count
# Filter cols: Year, Service are ID. Rest are Categories.
id_vars = ['Service', 'Year']
value_vars = [c for c in df.columns if c not in id_vars and c != 'Total'] # Exclude Total if present (CSV doesn't have it)

df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='Category', value_name='Count')

# Now proceed with previous logic
df = df_long
df = df[df['Year'].between(2020, 2025)]
df = df[df['Category'] != 'General Terms']

# Calculate totals
totals = df.groupby(['Service', 'Year'])['Count'].sum().reset_index().rename(columns={'Count': 'Total'})
df = df.merge(totals, on=['Service', 'Year'])
df['Share'] = (df['Count'] / df['Total']) * 100
df['Share'] = df['Share'].fillna(0)

colors = {
    'Content Licensing': 'tudablue',
    'Regulatory Compliance': 'tudagreen',
    'Technical Blocking': 'tudared',
    'Price Discrimination': 'cyan',
    'Legal Threat': 'orange'
}

marks = {
    'Content Licensing': 'square*',
    'Regulatory Compliance': 'triangle*',
    'Technical Blocking': 'x',
    'Price Discrimination': 'diamond*',
    'Legal Threat': 'pentagon*'
}

groups = {
    'Video': ['Netflix', 'YouTube Premium', 'Disney+', 'Amazon Prime'],
    'Software': ['Spotify', 'Apple Music', 'Microsoft', 'Adobe']
}

services = df['Service'].unique()
# print(f"Found services: {services}")

def generate_axis(service_name):
    print(f"        \\begin{{minipage}}{{0.48\\textwidth}}")
    print(f"            \\centering")
    print(f"            \\begin{{tikzpicture}}")
    print(f"                \\begin{{axis}}[")
    print(f"                    width=\\linewidth, height=5cm, xlabel={{Year}}, ylabel={{Share (\\%)}},")
    print(f"                    xmin=2020, xmax=2025, xtick={{2020,2022,2024}},")
    print(f"                    xticklabel style={{/pgf/number format/set thousands separator={{}}}},")
    print(f"                    grid=major, legend pos=north west, legend style={{font=\\tiny}},")
    # Escape underscores in service name for title? No, names are clean usually.
    display_title = service_name.replace('YouTube Premium', 'YouTube').replace('Amazon Prime', 'Amazon').replace('Apple Music', 'Apple')
    
    print(f"                    title={{{display_title}}}, title style={{font=\\footnotesize\\bfseries}},")
    print(f"                    ymin=0, ymax=100") 
    print(f"                ]")

    service_data = df[df['Service'] == service_name]
    if service_data.empty:
        # Try finding similar name?
        # Maybe 'Amazon' vs 'Amazon Prime' in CSV?
        pass

    all_years = pd.DataFrame({'Year': range(2020, 2026)})
    
    for cat, color in colors.items():
        cat_data = service_data[service_data['Category'] == cat]
        merged = all_years.merge(cat_data, on='Year', how='left').fillna(0)
        
        coords = ""
        for _, row in merged.iterrows():
            coords += f"({int(row['Year'])},{row['Share']:.1f}) "
            
        print(f"                    \\addplot[thick, color={color}, mark={marks[cat]}] coordinates {{ {coords} }}; \\addlegendentry{{{cat}}}")

    print(f"                \\end{{axis}}")
    print(f"            \\end{{tikzpicture}}")
    print(f"        \\end{{minipage}}")

# Fix for group mapping
# The CSV services are e.g. "Netflix", "YouTube Premium".
# The groups definition: ['Netflix', 'YouTube Premium'...] matches CSV service names?
# Let's hope so. If CSV has "Amazon" instead of "Amazon Prime", I should handle it.
# Step 41 showed "Amazon" in one place?
# "Amazon Live Table" or "Amazon Prime"?
# I'll enable fuzzy matching or manual map.

manual_map = {
    'Amazon': 'Amazon Prime', # If CSV says Amazon, map to Amazon Prime (group key)
    'YouTube': 'YouTube Premium',
    'Apple': 'Apple Music'
}
# Actually, I should map GROUP keys to CSV keys.
# CSV keys found (from step 41): "Microsoft", "Netflix", "Disney+".
# I'll check `services` content printed in previous run (it failed before printing).

# Revised: Just iterate group keys. Check if key in `services`. If not, try variations.
# But `services` is available at runtime.

# Open output file
with open('service_plots_new.tex', 'w', encoding='utf-8') as f:
    def print_to_file(s):
        f.write(s + '\n')

    print = print_to_file # Override print function

    print("% --- Generated Video Group ---")
    print("\\begin{figure}[ht]")
    print("    \\centering")
    for i, group_service in enumerate(groups['Video']):
        # Find matching CSV service
        csv_service = group_service
        if group_service not in services:
            # Try common variations
            if group_service == 'Amazon Prime' and 'Amazon' in services: csv_service = 'Amazon'
            elif group_service == 'YouTube Premium' and 'YouTube' in services: csv_service = 'YouTube'
        
        generate_axis(csv_service)
        if i % 2 == 0:
            print("    \\hfill")
        else:
            print("    \\vspace{0.5cm}")
    print("    \\caption{Strategic Evolution: Video Streaming Leaders (2020--2025). Grouping Netflix, YouTube, Disney+, and Amazon Prime.}")
    print("    \\label{fig:evol_video_main}")
    print("\\end{figure}")

    print("\n% --- Generated Software Group ---")
    print("\\begin{figure}[ht]")
    print("    \\centering")
    for i, group_service in enumerate(groups['Software']):
        csv_service = group_service
        if group_service not in services:
            if group_service == 'Apple Music' and 'Apple' in services: csv_service = 'Apple'
        
        generate_axis(csv_service)
        if i % 2 == 0:
            print("    \\hfill")
        else:
            print("    \\vspace{0.5cm}")
    print("    \\caption{Strategic Evolution: Music & Software (2020--2025). Grouping Spotify, Apple Music, Microsoft, and Adobe.}")
    print("    \\label{fig:evol_software_main}")
    print("\\end{figure}")
