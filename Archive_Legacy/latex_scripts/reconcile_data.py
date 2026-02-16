import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

def extract_coords(name, text_block):
    # (2020,41.6)
    return re.findall(r'\((\d{4}),([\d\.]+)\)', text_block)

print("--- Figure 6 (Global Priority Shift) ---")
# Axis 2: Incidents (N)
fig6_incidents = re.search(r'ylabel=\{Number of Incidents\}.*?coordinates \{(.*?)\}', text, re.DOTALL)
if fig6_incidents:
    print(f"Fig 6 Incidents: {extract_coords('Fig6', fig6_incidents.group(1))}")

print("\n--- Table 10 (Timeline Count) ---")
# Adobe & 2 & 0 & 0 & 0 & 1 & 1 \\
# YouTube Premium & 1 & 0 & 16 & 53 & 31 & 20 \\
# Note: User request says Table 10, but I see it as Table \ref{tab:timeline_count} in code (L1272)
tab_count = re.search(r'\\begin\{tabular\}\{l\|cccccc\}.*?\\end\{tabular\}', text, re.DOTALL)
if tab_count:
    rows = re.findall(r'(YouTube Premium|Netflix|Disney\+).*?& ([\d & ]+) \\\\', tab_count.group(0))
    for service, vals in rows:
        print(f"Tab 10 {service}: {vals.split('&')}")

print("\n--- Figure 12 (Evolution Video) ---")
# YouTube title={YouTube Premium} ... coordinates
fig12_blocks = re.findall(r'title=\{([a-zA-Z\+ ]+)\}.*?coordinates \{(.*?)\}', text, re.DOTALL)
for title, coords in fig12_blocks[:4]: # First 4 are video
    print(f"Fig 12 {title}: {extract_coords(title, coords)}")

print("\n--- Figure 11 (Timeline Service) ---")
fig11 = re.search(r'label\{fig:timeline_service_latex\}.*?coordinates \{(.*?)\}', text, re.DOTALL)
# This one has two addplots
fig11_plots = re.findall(r'\\addplot.*?coordinates \{(.*?)\}.*?\\legend\{(.*?)\}', text, re.DOTALL)
# Wait, Fig 11 has YouTube and Netflix
for coords, legend in fig11_plots:
    # This is rough, let's just grep the lines
    pass
