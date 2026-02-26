# MiniWorld DEX Source Analyzer - 分析DEX源码结构
$DEX_SOURCE = "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MiniWorld DEX Source Structure Analyzer"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. 查找所有子目录结构
Write-Host "[1] Analyzing directory structure..." -ForegroundColor Yellow
$dirs = Get-ChildItem -Path $DEX_SOURCE -Directory -Recurse | Select-Object -ExpandProperty FullName
Write-Host "Found $($dirs.Count) directories"

# 2. 查找可能的方块相关文件（多种命名模式）
Write-Host ""
Write-Host "[2] Searching for block-related files..." -ForegroundColor Yellow
$blockPatterns = @("*block*", "*Block*", "*BLOCK*", "*terrain*", "*Terrain*", "*item*", "*Item*", "*world*", "*World*")
$blockFiles = @()
foreach ($pattern in $blockPatterns) {
    $files = Get-ChildItem -Path $DEX_SOURCE -Filter "*.java" -Recurse | Where-Object { $_.Name -like $pattern }
    $blockFiles += $files
}
$blockFiles = $blockFiles | Select-Object -Unique | Select-Object -First 50
Write-Host "Found $($blockFiles.Count) potential block/item files"
$blockFiles | Select-Object Name, @{N="RelativePath";E={$_.FullName.Replace($DEX_SOURCE, "")}} | Format-Table -AutoSize

# 3. 搜索常量定义（放宽模式）
Write-Host ""
Write-Host "[3] Searching for ID constants..." -ForegroundColor Yellow
$allJavaFiles = Get-ChildItem -Path $DEX_SOURCE -Filter "*.java" -Recurse
$constants = @()

foreach ($file in $allJavaFiles | Select-Object -First 300) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        # 搜索所有 public static final int 定义
        $matches = [regex]::Matches($content, 'public\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+)')
        foreach ($match in $matches) {
            $varName = $match.Groups[1].Value
            $value = $match.Groups[2].Value
            # 过滤可能是方块ID的常量（值通常在0-500之间，或有特定命名）
            if ([int]$value -lt 1000 -and ($varName -match "block|Block|BLOCK|terrain|Terrain|id|Id|ID|type|Type")) {
                $constants += [PSCustomObject]@{
                    File = $file.Name
                    Variable = $varName
                    Value = $value
                    FullPath = $file.FullName.Replace($DEX_SOURCE, "")
                }
            }
        }
    } catch {
        # Skip files with errors
    }
}

# 去重并按值排序
$uniqueConstants = $constants | Sort-Object Value -Unique | Select-Object -First 100
Write-Host "Found $($uniqueConstants.Count) unique constants"

# 显示结果
Write-Host ""
Write-Host "Top constants found:" -ForegroundColor Green
$uniqueConstants | Group-Object Variable | Sort-Object Count -Descending | Select-Object -First 20 | Format-Table Name, Count -AutoSize

# 4. 按值分组显示
Write-Host ""
Write-Host "[4] Sample constants by value range:" -ForegroundColor Yellow
$uniqueConstants | Where-Object { [int]$_.Value -lt 100 } | Sort-Object Value | Format-Table Value, Variable, File -AutoSize

# 5. 导出详细结果
Write-Host ""
Write-Host "[5] Exporting detailed results..." -ForegroundColor Yellow
$output = @{
    scan_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    total_directories = $dirs.Count
    total_java_files = $allJavaFiles.Count
    block_related_files = $blockFiles | ForEach-Object { $_.FullName.Replace($DEX_SOURCE, "") }
    constants_found = $uniqueConstants | ForEach-Object { 
        @{ Variable = $_.Variable; Value = $_.Value; File = $_.File }
    }
}

$outputFile = "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\src\protocol\dex_structure_analysis.json"
$output | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding UTF8
Write-Host "Results saved to: $outputFile" -ForegroundColor Green

# 6. 建议搜索的关键词
Write-Host ""
Write-Host "[6] Recommended search keywords:" -ForegroundColor Cyan
$keywords = $uniqueConstants | Group-Object Variable | Sort-Object Count -Descending | Select-Object -First 10
$keywords | ForEach-Object {
    Write-Host "  - $($_.Name) (appears $($_.Count) times)" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Analysis complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan