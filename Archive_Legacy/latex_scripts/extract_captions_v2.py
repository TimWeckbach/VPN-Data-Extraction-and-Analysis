import re

def get_nested_content(text, start_pos):
    """Finds content inside curly braces, handling nesting."""
    depth = 0
    for i in range(start_pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start_pos+1:i]
    return None

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all \caption{
caption_starts = [m.start() for m in re.finditer(r'\\caption\{', content)]

with open('all_captions_verified.txt', 'w', encoding='utf-8') as f_out:
    for i, start in enumerate(caption_starts, 1):
        # The start of the content is at start + 8 (length of \caption{) - wait, regex is \caption\{
        # let's just pass start + len("\caption") - 1 = start + 8
        full_caption_content = get_nested_content(content, start + 8)
        f_out.write(f"Caption {i} (Index {start}):\n{full_caption_content}\n")
        f_out.write("-" * 20 + "\n")

print("Extracted verified captions.")
