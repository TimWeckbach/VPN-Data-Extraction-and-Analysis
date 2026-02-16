Start-Sleep -Seconds 60

$queries = @(
    "Business+models+business+strategy+and+innovation+Teece",
    "Price+discrimination+Varian+1989+Handbook+Industrial+Organization",
    "Business+models+Origin+development+future+research+perspectives+Wirtz",
    "The+business+model+Recent+developments+and+future+research+Zott",
    "Platform+envelopment+Eisenmann"
)

$keys = @(
    "teece2010business",
    "varian1989price",
    "wirtz2016business",
    "zott2011business",
    "eisenmann2011platform"
)

for ($i = 0; $i -lt $queries.Count; $i++) {
    $url = "https://api.semanticscholar.org/graph/v1/paper/search?query=$($queries[$i])&limit=1&fields=abstract,title,year"
    $key = $keys[$i]
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 15
        if ($response.total -gt 0) {
            $paper = $response.data[0]
            $title = $paper.title
            $year = $paper.year
            $abstract = $paper.abstract
            if ($abstract -and $abstract.Length -gt 0) {
                $firstSentence = ($abstract -split '\. ')[0] + "."
            } else {
                $firstSentence = "(no abstract)"
            }
            Write-Output "$key | VERIFIED | $title ($year) | $firstSentence"
        } else {
            Write-Output "$key | NOT FOUND | no results"
        }
    } catch {
        Write-Output "$key | ERROR | $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 5
}
