$ErrorActionPreference = "Stop"

Write-Host "--- STEP 1: Starting Classification with Gemini 3 Flash Preview ---" -ForegroundColor Cyan
python "Quantitative DATA\run_fast_categorization.py"

Write-Host "--- STEP 2: Generating Clean CSV Exports ---" -ForegroundColor Cyan
python "Quantitative DATA\generate_sheets_export.py"

Write-Host "--- PIPELINE COMPLETE ---" -ForegroundColor Green
Write-Host "The following files are ready for upload:"
Write-Host " - Quantitative DATA\Sheets_Import_DSPI.csv"
Write-Host " - Quantitative DATA\Sheets_Import_Qual_Counts.csv"
Write-Host " - Quantitative DATA\Sheets_Import_Qual_Timeline.csv"
Write-Host " - Quantitative DATA\Sheets_Import_Correlation.csv"
