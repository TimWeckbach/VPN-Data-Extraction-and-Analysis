import os

def fix_file(filename):
    try:
        # PowerShell > redirection often yields UTF-16LE
        with open(filename, 'r', encoding='utf-16') as f:
            content = f.read()
    except:
        try:
            # Fallback to UTF-8
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            # Fallback to system default
            with open(filename, 'r') as f:
                content = f.read()
    
    new_filename = filename.replace('.tex', '_clean.tex')
    with open(new_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filename} -> {new_filename}")

fix_file('service_plots.tex')
fix_file('distribution_plots.tex')
