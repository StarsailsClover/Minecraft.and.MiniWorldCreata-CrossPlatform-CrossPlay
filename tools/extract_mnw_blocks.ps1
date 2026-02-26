# 保存到: tools/extract_mnw_blocks.ps1
$DEX_SOURCE = "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources"
Write-Host "Scanning Java sources..."
$files = gci $DEX_SOURCE -r -fi "*.java"
$patterns = @("BLOCK_\w+\s*=\s*\d+", "TERRAIN_\w+\s*=\s*\d+")
$results = @()
foreach ($f in $files | select -first 200) {
    $c = gc $f.FullName -Raw
    foreach ($p in $patterns) {
        [regex]::Matches($c, $p) | %{ $results += @{File=$f.Name; Match=$_.Value} }
    }
}
$results | select -first 50 | ft
$results | ConvertTo-Json | Out-File extracted_blocks.json