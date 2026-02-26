@echo off
echo ============================================
echo MiniWorld Block ID Extractor (Subdirs)
echo ============================================
echo.

set DEX_ROOT=C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources
set OUTPUT=C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\src\protocol\extracted_block_ids.json

echo [*] Scanning subdirectories in: %DEX_ROOT%
echo.

powershell -ExecutionPolicy Bypass -NoProfile -Command ^
"$root = '%DEX_ROOT%'; " ^
"$subdirs = Get-ChildItem -Path $root -Directory; " ^
"Write-Host ('Found ' + $subdirs.Count + ' subdirectories:'); " ^
"$subdirs | ForEach-Object { Write-Host ('  - ' + $_.Name) }; " ^
"Write-Host ''; " ^
"$allFiles = @(); " ^
"foreach ($dir in $subdirs) { " ^
"    $files = Get-ChildItem -Path $dir.FullName -Filter '*.java' -Recurse -ErrorAction SilentlyContinue; " ^
"    Write-Host ('Scanning ' + $dir.Name + ': ' + $files.Count + ' files'); " ^
"    $allFiles += $files; " ^
"} " ^
"Write-Host (''); " ^
"Write-Host ('Total Java files: ' + $allFiles.Count); " ^
"Write-Host (''); " ^
"$results = @(); " ^
"$processed = 0; " ^
"foreach ($f in $allFiles) { " ^
"    $processed++; " ^
"    if ($processed %% 100 -eq 0) { Write-Host ('  Processed ' + $processed + '/' + $allFiles.Count + '...') -ForegroundColor DarkGray; } " ^
"    try { " ^
"        $c = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue; " ^
"        if (-not $c) { continue; } " ^
"        $m = [regex]::Matches($c, 'static\s+final\s+int\s+(\w+)\s*=\s*(\d+)'); " ^
"        foreach ($match in $m) { " ^
"            $name = $match.Groups[1].Value; " ^
"            $val = [int]$match.Groups[2].Value; " ^
"            if ($val -ge 0 -and $val -le 1000 -and ($name -match 'BLOCK|block|Block|ID|Id|Type|TYPE|type|TERRAIN|Terrain|terrain')) { " ^
"                $results += @{File=$f.Name; Path=$f.FullName.Replace($root, ''); Variable=$name; ID=$val}; " ^
"            } " ^
"        } " ^
"    } catch {} " ^
"} " ^
"Write-Host (''); " ^
"Write-Host ('Found ' + $results.Count + ' potential block ID definitions'); " ^
"$uniqueById = $results | Sort-Object ID -Unique | Select-Object -First 200; " ^
"Write-Host ('Unique IDs: ' + $uniqueById.Count); " ^
"$output = @{timestamp=Get-Date -Format 'yyyy-MM-dd HH:mm:ss'; total_files=$allFiles.Count; matches_found=$results.Count; unique_ids=$uniqueById.Count; candidates=$uniqueById}; " ^
"$output | ConvertTo-Json -Depth 10 | Out-File '%OUTPUT%' -Encoding UTF8; " ^
"Write-Host (''); " ^
"Write-Host ('[+] Results saved to: %OUTPUT%') -ForegroundColor Green; " ^
"Write-Host (''); " ^
"Write-Host ('Sample results (first 20):') -ForegroundColor Cyan; " ^
"$uniqueById | Select-Object -First 20 | Format-Table ID, Variable, File -AutoSize"

echo.
pause