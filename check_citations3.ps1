Start-Sleep -Seconds 90

$queries = @(
    "Business+models+business+strategy+and+innovation+Teece+2010",
    "Price+discrimination+Varian+1989",
    "Business+models+Origin+development+future+research+perspectives+Wirtz+2016",
    "The+business+model+Recent+developments+and+future+research+Zott+Amit",
    "Examining+how+Great+Firewall+discovers+hidden+circumvention+servers+Ensafi",
    "Digital+piracy+Theory+Belleflamme+Peitz",
    "Designing+conducting+mixed+methods+research+Creswell+2017",
    "business+of+platforms+Cusumano+2019",
    "Netflix+nations+geography+digital+distribution+Lobato"
)

$keys = @(
    "teece2010business",
    "varian1989price",
    "wirtz2016business",
    "zott2011business",
    "ensafi2015examining",
    "belleflamme2015piracy",
    "creswell2017designing",
    "cusumano2019platform",
    "lobato2019geoblocking"
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
