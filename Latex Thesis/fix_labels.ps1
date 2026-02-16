$file = "main.tex"
$content = Get-Content $file -Raw

# Fix duplicate label: tab:correlation_data (second occurrence only - in detailed section)
# The second table has "Pearson" in the caption, use that to target it specifically
$content = $content -replace '(Pearson.*?\n\s*\\label\{)tab:correlation_data(\})', '$1tab:correlation_data_detailed$2'

# Fix duplicate label: fig:fortress_index (second occurrence - in detailed analysis section near "Measured Enforcement")  
$content = $content -replace '(Measured Enforcement Intensity by Service.*?\n\s*\\label\{)fig:fortress_index(\})', '$1fig:fortress_index_detailed$2'

# Fix duplicate label: fig:category_dist_viz (second occurrence - near "nodes near coords align")
$content = $content -replace '(nodes near coords align=\{horizontal\},\s*\n\s*xmin=0,\s*\n\s*bar width=15pt,\s*\n\s*yticklabel style=\{font=\\footnotesize\},\s*\n\s*\]\s*\n\s*\\addplot\[fill=tudablue\] coordinates \{.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n\s*\\end\{axis\}\s*\n\s*\\end\{tikzpicture\}\s*\n\s*\\caption\{Proportional Distribution of Enforcement Categories \(Aggregate\)\}\s*\n\s*\\label\{)fig:category_dist_viz(\})', '$1fig:category_dist_viz_detailed$2'

# Fix caption with unescaped &
$content = $content -replace '(\\caption\{Strategic Evolution: Music) & (Software)', '$1 \& $2'

# Fix undefined ref fig:priority_shift_latex -> remove the reference since no such figure exists
$content = $content -replace 'as previously detailed in Figure \\ref\{fig:priority_shift_latex\} and Table', 'as previously detailed in Table'

# Fix undefined ref tab:category_dist -> use tab:qual_timeline_complete which exists
$content = $content -replace '\\ref\{tab:category_dist\}', '\ref{tab:qual_timeline_complete}'

# Fix undefined ref fig:evol_amazon -> use fig:evol_video_main  
$content = $content -replace '\\ref\{fig:evol_amazon\}', '\ref{fig:evol_video_main}'

# Fix undefined ref fig:evol_apple_music -> use fig:evol_software_main
$content = $content -replace '\\ref\{fig:evol_apple_music\}', '\ref{fig:evol_software_main}'

Set-Content $file $content -NoNewline
Write-Host "Done fixing labels"
