@echo off
echo ============================================
echo MiniWorld Block ID Extractor (Simple Mode)
echo ============================================
echo.

set DEX=C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources
set OUTPUT=C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\src\protocol\extracted_simple.json

echo [*] Scanning Java files in DEX source...
echo     Source: %DEX%
echo.

powershell -ExecutionPolicy Bypass -NoProfile -Command ^
"$files = Get-ChildItem -Path '%DEX%' -Filter '*.java' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 200; " ^
"$results = @(); " ^
"foreach ($f in $files) { " ^
"    try { " ^
"        $c = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue; " ^
"        $m = [regex]::Matches($c, 'static\s+final\s+int\s+(\w+)\s*=\s*(\d+)'); " ^
"        foreach ($match in $m) { " ^
"            $val = [int]$match.Groups[2].Value; " ^
"            if ($val -lt 500) { " ^
"                $results += @{File=$f.Name; Name=$match.Groups[1].Value; ID=$val}; " ^
"            } " ^
"        } " ^
"    } catch {} " ^
"} " ^
"$results | Sort-Object ID -Unique | Select-Object -First 100 | ConvertTo-Json | Out-File '%OUTPUT%' -Encoding UTF8; " ^
"Write-Host ('[+] Found ' + $results.Count + ' matches'); " ^
"Write-Host ('[+] Saved to: %OUTPUT%')"

echo.
echo Script completed.
pause