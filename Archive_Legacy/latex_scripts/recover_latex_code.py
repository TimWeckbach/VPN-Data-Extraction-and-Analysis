import re
import os

# Use raw string with single backslashes for Windows path
log_path = r'C:\Users\Titan\.gemini\antigravity\brain\659a16de-b5f4-47bf-abc5-101c3b61357d\.system_generated\logs\applying_thesis_updates.txt'

def parse_log_for_figures(path):
    print(f"Scanning {path}...")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        # Try alternate path just in case
        alt_path = 'applying_thesis_updates.txt'
        if os.path.exists(alt_path):
             path = alt_path
             print(f"DeepScan: Found local log {path}")
        else:
             return {}

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error: {e}")
        return {}

    found = {}
    
    targets = [
        'fig:frames_evolution_latex',
        'fig:service_dist_latex',
        'fig:fortress_index_latex',
        'fig:dspi_map',
        'fig:affordability'
    ]
    
    # Improved extraction logic
    for t in targets:
        # Search for label
        # We search specifically for ReplacementContent that contains the label.
        # But logs are unstructured mostly.
        # We search for "\label{t}"
        
        search_term = r'\label{' + t + r'}'
        idx = content.rfind(search_term)
        
        if idx != -1:
            # Found the label. Now find the enclosing figure environment.
            # Search backwards for \begin{figure} relative to idx.
            
            # Safe distance limit? 5000 chars?
            min_idx = max(0, idx - 5000)
            
            start_fig = content.rfind(r'\begin{figure}', min_idx, idx)
            
            # Search forwards for \end{figure}
            end_fig = content.find(r'\end{figure}', idx)
            
            if start_fig != -1 and end_fig != -1:
                # Extract
                raw_code = content[start_fig:end_fig+12] # +12 for \end{figure}
                
                # Cleanup:
                # Remove json escapes
                clean_code = raw_code.replace('\\\\', '\\').replace('\\"', '"').replace('\\n', '\n')
                
                # Further cleanup: if it was inside a json string, " might be escaped.
                # If the log format is: "ReplacementContent": "..."
                # Then actual content ignores starting/ending quotes?
                # But here we just extract string.
                
                if r'\begin{figure}' in clean_code:
                    found[t] = clean_code
                    print(f"Recovered {t} (len {len(clean_code)})")
                else:
                    print(f"Extraction failed integrity check for {t}")
            else:
                 print(f"Found {t} at {idx} but could not find surrounding figure block.")
        else:
            print(f"Could not find {t} in log.")

    return found

figures = parse_log_for_figures(log_path)

if not figures:
    print("No figures found.")

# Save to file
with open('recovered_figures.tex', 'w', encoding='utf-8') as f:
    for k, v in figures.items():
        f.write(f"% --- {k} ---\n")
        f.write(v)
        f.write("\n\n")

print("Saved recovered_figures.tex")
