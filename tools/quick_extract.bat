@echo off
echo ============================================
echo Quick Block ID Extractor
echo ============================================
echo.

set DEX_ROOT=C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources
set OUTPUT=C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\src\protocol\block_ids_found.json

echo [*] Quick scan of DEX subdirectories...
echo.

powershell -ExecutionPolicy Bypass -Command "& {"
powershell -Command "$root='%DEX_ROOT%'; $files=gci $root -r -fi '*.java'; Write-Host \"Files: $($files.Count)\"; $r=@(); foreach($f in $files|Select -First 300){$c=gc $f -Raw -EA SilentlyContinue; $m=[regex]::Matches($c,'static\s+final\s+int\s+(\w+)\s*=\s*(\d+)'); foreach($x in $m){$v=[int]$x.Groups[2].Value;if($v-lt500-and($x.Groups[1].Value-match'BLOCK|block|Block|ID|Id')){$r+=@{ID=$v;Name=$x.Groups[1].Value;File=$f.Name}}}}; $u=$r|sort ID -Unique|Select -First 100; Write-Host \"Found: $($r.Count) matches, $($u.Count) unique\"; $u|Select -First 30|ft ID,Name,File -AutoSize; @{candidates=$u}|ConvertTo-Json|Out-File '%OUTPUT%'; Write-Host \"Saved to: %OUTPUT%\"}"

echo.
pause