$path = "C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
$lines = [System.IO.File]::ReadAllLines($path)
$lines[1020] = $lines[1020].Replace('tab:correlation_data', 'tab:correlation_data_detailed')
$lines[1198] = $lines[1198].Replace('fig:category_dist_viz', 'fig:category_dist_viz_detailed')
[System.IO.File]::WriteAllLines($path, $lines)
Write-Host "Fixed 2 labels"
