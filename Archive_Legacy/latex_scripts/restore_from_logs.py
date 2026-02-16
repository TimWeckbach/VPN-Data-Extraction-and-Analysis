import re
import os

log_path = r'C:\Users\Titan\.gemini\antigravity\brain\659a16de-b5f4-47bf-abc5-101c3b61357d\.system_generated\logs\applying_thesis_updates.txt'
output_path = 'main_restored.tex'

# Content dictionary: line_number -> text
file_content = {}

def parse_log(path):
    print(f"Reading log: {path}")
    if not os.path.exists(path):
        print("Log file not found!")
        return

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    capturing = False
    captured_count = 0
    
    for line in lines:
        # Detect start of view_file output for main.tex
        if "File Path:" in line and "main.tex" in line:
            # We are in a view_file block for main.tex.
            # But the content follows "The following code has been modified..."
            pass
        
        if "The following code has been modified to include a line number" in line:
            capturing = True
            continue
            
        if capturing:
            # Check for end of block
            if "The above content does NOT show the entire file contents" in line or "Step Id:" in line:
                capturing = False
                continue
                
            # Parse line: "\d+: content"
            # Regex match
            match = re.match(r'^(\d+): (.*)', line)
            if match:
                lineno = int(match.group(1))
                content = match.group(2)
                file_content[lineno] = content
                captured_count += 1
            else:
                # Maybe empty line or wrapping?
                # Usually view_file output keeps format.
                pass

    print(f"Captured {len(file_content)} unique lines.")

parse_log(log_path)

# Depending on if we have lines 1 to End
if not file_content:
    print("No content found.")
    exit(1)

max_line = max(file_content.keys())
print(f"Max line number: {max_line}")

# Fill missing lines?
# If we missed some lines, they will be empty.
# We should list missing chunks.
missing = []
for i in range(1, max_line + 1):
    if i not in file_content:
        missing.append(i)

if missing:
    print(f"Missing lines: {len(missing)}")
    # Simplify display of ranges
    ranges = []
    if missing:
        start = missing[0]
        prev = missing[0]
        for x in missing[1:]:
            if x != prev + 1:
                ranges.append((start, prev))
                start = x
            prev = x
        ranges.append((start, prev))
    print(f"Missing ranges: {ranges}")
else:
    print("All lines 1 to Max present.")

# Write restored file
with open(output_path, 'w', encoding='utf-8') as f:
    for i in range(1, max_line + 1):
        line = file_content.get(i, "") # Empty string if missing
        f.write(line + '\n')

print(f"Wrote {output_path}")
