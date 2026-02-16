$path = "C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Latex Thesis\main.tex"
$c = [System.IO.File]::ReadAllText($path)
$c = $c.Replace('tab:correlation_data_detailed_detailed', 'tab:correlation_data_detailed')
[System.IO.File]::WriteAllText($path, $c)
Write-Host "Fixed"
