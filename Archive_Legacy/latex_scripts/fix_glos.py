import re

file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tags = ['dspi', 'tos', 'vpn', 'rq', 'bmi']

for tag in tags:
    # 1. Standardize \gls{tag} and \glspl{tag} by fixing common truncation/doubling
    # Fix \gls{tag (missing close)
    content = content.replace('\\gls{' + tag + ' ', '\\gls{' + tag + '} ')
    content = content.replace('\\gls{' + tag + ',', '\\gls{' + tag + '},')
    content = content.replace('\\gls{' + tag + '.', '\\gls{' + tag + '}.')
    content = content.replace('\\gls{' + tag + ')', '\\gls{' + tag + '})')
    content = content.replace('\\gls{' + tag + '\n', '\\gls{' + tag + '}\n')
    
    # Fix \glspl{tag
    content = content.replace('\\glspl{' + tag + ' ', '\\glspl{' + tag + '} ')
    content = content.replace('\\glspl{' + tag + ',', '\\glspl{' + tag + '},')
    content = content.replace('\\glspl{' + tag + '.', '\\glspl{' + tag + '}.')
    content = content.replace('\\glspl{' + tag + ')', '\\glspl{' + tag + '})')
    content = content.replace('\\glspl{' + tag + '\n', '\\glspl{' + tag + '}\n')

# 2. Specifically target the caption issues found in all_captions.txt
content = content.replace('Average \\gls{dspi', 'Average \\gls{dspi}')
content = content.replace('Digital Services Price Index (\\gls{dspi', 'Digital Services Price Index (\\gls{dspi})')
content = content.replace('Categories in \\gls{tos', 'Categories in \\gls{tos}')
content = content.replace('Analyzed \\gls{tos', 'Analyzed \\gls{tos}')

# 3. Clean up the abstract/keyword double braces I might have introduced
for tag in tags:
    content = content.replace('\\gls{' + tag + '}}', '\\gls{' + tag + '}')
    content = content.replace('\\glspl{' + tag + '}}', '\\glspl{' + tag + '}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed GLOS commands.")
