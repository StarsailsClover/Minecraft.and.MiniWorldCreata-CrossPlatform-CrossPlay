# MiniWorld Block ID Extractor v2 - 优化版
$DEX_SOURCE = "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources"
$OUTPUT_FILE = "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\src\protocol\extracted_block_ids_v2.json"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MiniWorld Block ID Extractor v2"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查目录
if (-not (Test-Path $DEX_SOURCE)) {
    Write-Host "[-] Error: Source directory not found!" -ForegroundColor Red
    exit 1
}

# 获取所有Java文件
$javaFiles = Get-ChildItem -Path $DEX_SOURCE -Filter "*.java" -Recurse
Write-Host "[*] Found $($javaFiles.Count) Java files" -ForegroundColor Yellow

# 定义更宽松的提取模式
$extractionPatterns = @(
    @{
        Name = "Standard constants"
        Regex = 'public\s+static\s+final\s+(?:int|short)\s+(\w+)\s*=\s*(\d+)'
    },
    @{
        Name = "Static fields"
        Regex = 'static\s+(?:final\s+)?(?:int|short)\s+(\w+)\s*=\s*(\d+)'
    },
    @{
        Name = "Enum values"
        Regex = '(\w+)\s*\(\s*(\d+)\s*\)'
    },
    @{
        Name = "Array indices"
        Regex = '\[\s*(\d+)\s*\].*=.*new\s+Block|Block\[\s*(\d+)\s*\]'
    }
)

$allMatches = @()

# 针对每个文件进行扫描
$fileCounter = 0
foreach ($file in $javaFiles | Select-Object -First 500) {
    $fileCounter++
    if ($fileCounter % 100 -eq 0) {
        Write-Host "  Processed $fileCounter files..." -ForegroundColor DarkGray
    }
    
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        
        # 只处理可能包含方块定义的文件
        $isBlockFile = $content -match "block|Block|BLOCK|terrain|Terrain|world|World|item|Item" -and 
                       $content -match "class|enum|interface"
        
        if (-not $isBlockFile) { continue }
        
        foreach ($pattern in $extractionPatterns) {
            $matches = [regex]::Matches($content, $pattern.Regex, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            
            foreach ($match in $matches) {
                $name = $match.Groups[1].Value
                $value = $match.Groups[2].Value
                
                # 验证和过滤
                if (-not $name -or -not $value) { continue }
                
                # 尝试转换为整数
                try {
                    $intValue = [int]$value
                    
                    # 只保留可能是方块ID的值（通常在合理范围内）
                    if ($intValue -ge 0 -and $intValue -le 1000 -and $name -match "^[a-zA-Z_][a-zA-Z0-9_]*$") {
                        $allMatches += [PSCustomObject]@{
                            FileName = $file.Name
                            RelativePath = $file.FullName.Replace($DEX_SOURCE, "").TrimStart("\")
                            VariableName = $name
                            ID = $intValue
                            PatternType = $pattern.Name
                            Content = if ($name.Length -lt 30) { 
                                ($content.Substring([Math]::Max(0, $match.Index - 50), [Math]::Min(100, $content.Length - $match.Index))) -replace "`r`n", " "
                            } else { "" }
                        }
                    }
                } catch {
                    # Skip non-integer values
                }
            }
        }
    }
    catch {
        Write-Host "  [!] Error reading $($file.Name): $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[+] Found $($allMatches.Count) total matches" -ForegroundColor Green

# 按ID分组统计
Write-Host ""
Write-Host "[*] Analyzing results..." -ForegroundColor Yellow
$idGroups = $allMatches | Group-Object ID | Sort-Object Name -Property {[int]$_.Name}

# 找到最可能是方块定义的变量名
$candidates = $allMatches | Where-Object { 
    $_.VariableName -match "block|Block|BLOCK|terrain|Terrain|ID|Id|Type|TYPE|type" -and
    $_.ID -lt 500
} | Sort-Object ID -Unique | Select-Object -First 200

Write-Host ""
Write-Host "[+] Found $($candidates.Count) potential block ID candidates" -ForegroundColor Green

# 显示前50个候选
Write-Host ""
Write-Host "Top 50 Block ID Candidates:" -ForegroundColor Cyan
$candidates | Select-Object -First 50 | Format-Table ID, VariableName, FileName, @{N="Snippet";E={$_.Content.Substring(0, [Math]::Min(50, $_.Content.Length))}} -AutoSize

# 按ID顺序显示
Write-Host ""
Write-Host "Candidates by ID (0-100):" -ForegroundColor Cyan
$candidates | Where-Object { $_.ID -lt 100 } | Sort-Object ID | Format-Table ID, VariableName, FileName -AutoSize

# 导出到JSON
$result = @{
    extraction_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    source_directory = $DEX_SOURCE
    total_files_scanned = $fileCounter
    total_matches = $allMatches.Count
    candidate_count = $candidates.Count
    candidates = @($candidates | ForEach-Object {
        @{
            mnw_id = $_.ID
            variable_name = $_.VariableName
            file = $_.FileName
            path = $_.RelativePath
            context = $_.Content.Substring(0, [Math]::Min(100, $_.Content.Length))
        }
    })
    id_distribution = @($idGroups | Where-Object { [int]$_.Name -lt 200 } | ForEach-Object {
        @{ ID = $_.Name; Count = $_.Count }
    })
}

# 保存结果
$result | ConvertTo-Json -Depth 10 | Out-File $OUTPUT_FILE -Encoding UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Results saved to: $OUTPUT_FILE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

# 提供帮助信息
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review the candidates in the JSON file" -ForegroundColor White
Write-Host "  2. Identify the actual block IDs by variable naming conventions" -ForegroundColor White
Write-Host "  3. Update block_mapping_template.json with found IDs" -ForegroundColor White
Write-Host ""
Write-Host "Common patterns in MiniWorld DEX:" -ForegroundColor Yellow
Write-Host "  - Look for variables like: BLOCK_STONE, BLOCK_DIRT, BLOCK_GRASS" -ForegroundColor White
Write-Host "  - Or: ID_STONE, TYPE_Dirt, TERRAIN_ID_" -ForegroundColor White
Write-Host "  - Or enum values with numeric assignments" -ForegroundColor White