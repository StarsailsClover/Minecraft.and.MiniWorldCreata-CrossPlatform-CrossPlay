# MiniWorld DEX 方块ID手动搜索指南

## 已知信息

从之前DEX字符串分析中，我们发现了：
- **服务器地址**: `ws://wskacchm.mini1.cn:4000` (游戏逻辑服务器)
- **认证**: HTTPS API 到 `mwu-api-pre.mini1.cn`
- **证书**: DigiCert Global Root CA, GlobalSign, RapidSSL

## 推荐的搜索策略

### 1. 直接文件搜索

在反编译的Java源码目录中搜索：

```powershell
$DEX = "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources"

# 搜索包含 "Block" 或 "block" 的类定义
Get-ChildItem -Path $DEX -Filter "*.java" -Recurse | 
    Select-String -Pattern "class.*Block|enum.*Block" | 
    Select-Object -First 30

# 搜索整数常量定义（所有可能的ID）
Get-ChildItem -Path $DEX -Filter "*.java" -Recurse |
    Select-String -Pattern "public static final int\s+\w+\s*=\s*\d+" |
    Select-Object -First 100

# 搜索特定模式
$patterns = @(
    "STONE\s*=\s*\d+",
    "DIRT\s*=\s*\d+",
    "GRASS\s*=\s*\d+",
    "BLOCK_\w+\s*=\s*\d+",
    "TERRAIN_\w+\s*=\s*\d+"
)

foreach ($p in $patterns) {
    Write-Host "`nSearching for: $p" -ForegroundColor Cyan
    Get-ChildItem -Path $DEX -Filter "*.java" -Recurse |
        Select-String -Pattern $p |
        Select-Object -First 5
}
```

### 2. 常见中文命名搜索

迷你世界是中国游戏，可能使用中文字符串或拼音：

```powershell
# 可能的中文或拼音命名
$chinesePatterns = @(
    "shitou|石头",      # stone
    "tu|土",            # dirt
    "cao|草",           # grass
    "shazi|沙子",       # sand
    "yuankuang|矿石",   # ore
    "fangkuai|方块"     # block
)

foreach ($p in $chinesePatterns) {
    Get-ChildItem -Path $DEX -Filter "*.java" -Recurse |
        Select-String -Pattern $p -CaseSensitive:$false |
        Select-Object FileName, LineNumber, Line -First 3
}
```

### 3. 网络包分析辅助

已知服务器通信可能在 `ws/WsClient` 或 `network` 包中，可以：

1. 查找这些类中发送/接收方块数据的代码
2. 跟踪 ID 的使用位置
3. 确定 ID 的数值范围

### 4. 枚举类型检查

方块ID通常存储在枚举中：

```powershell
Get-ChildItem -Path $DEX -Filter "*.java" -Recurse |
    Select-String -Pattern "enum\s+\w*[Bb]lock\w*|enum\s+\w*[Tt]errain\w*" |
    Select-Object FileName, LineNumber, Line
```

### 5. 如果没有找到标准模式

可能是以下情况之一：

a) **ID存储在资源文件而不是类中** - 检查 assets/ 目录
b) **ID在运行时动态分配** - 需要运行时分析
c) **类名被混淆了** - 查找无意义类名（如 a.java, b.java）
d) **使用反射或 native 代码** - 需要更深入分析

## 备选方案

如果DEX源码中没有找到方块ID：

1. **抓包分析** - 在捕获的 WebSocket 数据中寻找方块放置/破坏的包
2. **内存转储分析** - 使用 Frida 在运行时 hook 方块相关函数
3. **APK资源文件** - 检查 assets/blocks.json 或类似文件
4. **游戏客户端 Hook** - 拦截 getBlockId() 等函数

## 立即行动计划

请运行以下命令并粘贴结果：

```powershell
# 1. 查看Java源码目录结构
Get-ChildItem "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources" -Directory | Select-Object -First 10

# 2. 查看最大的几个Java文件（可能包含核心逻辑）
Get-ChildItem "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources" -Filter "*.java" -Recurse |
    Sort-Object Length -Descending |
    Select-Object Name, @{N="SizeKB";E={[math]::Round($_.Length/1KB,2)}}, @{N="Path";E={$_.DirectoryName.Replace($DEX, "")}} -First 20

# 3. 搜索任何包含 "0, 1, 2" 等连续数字的文件（可能是ID列表）
Get-ChildItem "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\java_sources" -Filter "*.java" -Recurse |
    Select-String -Pattern "= 0;|= 1;|= 2;|= 3;|= 4;" |
    Group-Object FileName |
    Sort-Object Count -Descending |
    Select-Object -First 10
```

运行这些命令后，告诉我结果，我可以进一步指导如何提取准确的方块ID。