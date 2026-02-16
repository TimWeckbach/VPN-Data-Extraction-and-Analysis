file_path = r"c:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Truncated versions in captions the user mentioned or seen in extract_captions.txt
text = text.replace('\\gls{dspi\n', '\\gls{dspi}\n')
text = text.replace('\\gls{dspi ', '\\gls{dspi} ')
text = text.replace('\\gls{tos\n', '\\gls{tos}\n')
text = text.replace('\\gls{tos ', '\\gls{tos} ')
text = text.replace('\\gls{vpn\n', '\\gls{vpn}\n')
text = text.replace('\\gls{vpn ', '\\gls{vpn} ')

# Handle the specific artifacts of my previous botched multi-replacements
text = text.replace('\\gls{dspi}}', '\\gls{dspi}')
text = text.replace('\\gls{tos}}', '\\gls{tos}')
text = text.replace('\\gls{vpn}}', '\\gls{vpn}')
text = text.replace('\\gls{rq}}', '\\gls{rq}')
text = text.replace('\\gls{bmi}}', '\\gls{bmi}')

# Check for double braces anywhere else
keywords = ['dspi', 'tos', 'vpn', 'rq', 'bmi', 'ppp']
for kw in keywords:
    # Fix triple or double braces
    text = text.replace('\\gls{' + kw + '}}}', '\\gls{' + kw + '}')
    text = text.replace('\\gls{' + kw + '}}', '\\gls{' + kw + '}')
    text = text.replace('\\glspl{' + kw + '}}}', '\\glspl{' + kw + '}')
    text = text.replace('\\glspl{' + kw + '}}', '\\glspl{' + kw + '}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Final Glossaries Cleanup Done.")
