$queries = @(
    @{key="karimi2020strategic"; q="Karimi+strategic+agility+business+model+innovation+firm+performance"},
    @{key="kastanakis2012between"; q="Between+the+mass+and+the+class+Kastanakis"},
    @{key="masnick2019splinternet"; q="Splinternet+already+here+Masnick"},
    @{key="oberholzer2007effect"; q="effect+file+sharing+record+sales+Oberholzer-Gee"},
    @{key="pakko2003burgernomics"; q="Burgernomics+Big+Mac+purchasing+power+parity+Pakko"},
    @{key="ransbotham2009choice"; q="Choice+chance+conceptual+model+information+security+compromise+Ransbotham"},
    @{key="reidenberg2015privacy"; q="Privacy+harms+effectiveness+notice+choice+framework+Reidenberg"},
    @{key="reimers2016effect"; q="private+copyright+protection+effective+book+publishing+Reimers"},
    @{key="rochet2003platform"; q="Platform+competition+two-sided+markets+Rochet"},
    @{key="rogoff1996ppp"; q="purchasing+power+parity+puzzle+Rogoff"},
    @{key="stiglitz2008economic"; q="Economic+foundations+intellectual+property+rights+Stiglitz"},
    @{key="sundararajan2004managing"; q="Managing+digital+piracy+pricing+protection+Sundararajan"},
    @{key="sykes1957techniques"; q="Techniques+neutralization+theory+delinquency+Sykes"},
    @{key="teece2010business"; q="Business+models+business+strategy+innovation+Teece"},
    @{key="varian1989price"; q="Price+discrimination+Varian+Handbook+Industrial+Organization"},
    @{key="wirtz2016business"; q="Business+models+origin+development+future+research+Wirtz"},
    @{key="zott2011business"; q="business+model+recent+developments+future+research+Zott"},
    @{key="eisenmann2011platform"; q="Platform+envelopment+Eisenmann"},
    @{key="creswell2017designing"; q="Designing+conducting+mixed+methods+research+Creswell"},
    @{key="cusumano2019platform"; q="business+of+platforms+Cusumano"},
    @{key="lobato2019geoblocking"; q="Netflix+nations+geography+digital+distribution+Lobato"},
    @{key="osterwalder2010business"; q="Business+model+generation+Osterwalder"},
    @{key="shapiro1998information"; q="Information+rules+strategic+guide+network+economy+Shapiro"},
    @{key="srnicek2017platform"; q="Platform+capitalism+Srnicek"},
    @{key="tirole1988theory"; q="theory+industrial+organization+Tirole"},
    @{key="ensafi2015examining"; q="Great+Firewall+discovers+hidden+circumvention+servers+Ensafi"},
    @{key="belleflamme2015piracy"; q="Digital+piracy+theory+Belleflamme"}
)

$baseUrl = "https://api.semanticscholar.org/graph/v1/paper/search"
$results = @()

foreach ($item in $queries) {
    $url = "$baseUrl`?query=$($item.q)&limit=3&fields=abstract,title,year,authors"
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        $results += @{key=$item.key; data=$response.data; error=$null}
        Write-Host "OK: $($item.key)"
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $results += @{key=$item.key; data=$null; error="HTTP $statusCode"}
        Write-Host "FAIL ($statusCode): $($item.key)"
    }
    Start-Sleep -Seconds 4
}

$output = foreach ($r in $results) {
    $key = $r.key
    if ($r.error) {
        "=== $key === ERROR: $($r.error)"
    } else {
        $papers = $r.data
        $lines = @("=== $key ===")
        $i = 0
        foreach ($p in $papers) {
            $i++
            $authorNames = ($p.authors | ForEach-Object { $_.name }) -join "; "
            $abstract = if ($p.abstract) { $p.abstract.Substring(0, [Math]::Min(500, $p.abstract.Length)) } else { "N/A" }
            $lines += "  [$i] Title: $($p.title)"
            $lines += "      Year: $($p.year)"
            $lines += "      Authors: $authorNames"
            $lines += "      Abstract: $abstract"
        }
        $lines -join "`n"
    }
}

$output | Out-File -FilePath "citation_results.txt" -Encoding UTF8
Write-Host "`nDone. Results written to citation_results.txt"
