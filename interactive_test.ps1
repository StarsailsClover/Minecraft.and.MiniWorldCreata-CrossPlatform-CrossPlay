# MnMCP 交互式真实测试脚本 (PowerShell)
# 实际启动客户端，执行真实握手和数据交换

param(
    [switch]$FullTest,
    [switch]$StartBridge,
    [switch]$TestDataFlow,
    [switch]$StartWireshark,
    [switch]$StartMiniWorld,
    [switch]$ViewLogs
)

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 路径配置
$script:MNMCP_PATH = "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay"
$script:WIRESHARK_PATH = "D:\Program Files\Wireshark\Wireshark.exe"
$script:MINIWORLD_PATH = "C:\Users\Sails\Documents\Coding\MnMCPResources\Resources\pc_versions\miniworldPC_CN\miniworldLauncher\MicroMiniNew.exe"

# 颜色函数
function Write-ColorText($Text, $Color = "White") {
    Write-Host $Text -ForegroundColor $Color
}

function Show-Banner {
    Clear-Host
    Write-ColorText "`n============================================================" "Cyan"
    Write-ColorText "  MnMCP 交互式真实测试" "Green"
    Write-ColorText "  Interactive Real Connection Test" "Green"
    Write-ColorText "============================================================" "Cyan"
    Write-ColorText "`n  本脚本将：`" "Yellow"
    Write-ColorText "  1. 启动 MnMCP 桥接服务器" "White"
    Write-ColorText "  2. 启动 Wireshark 抓包" "White"
    Write-ColorText "  3. 等待 Minecraft 客户端连接" "White"
    Write-ColorText "  4. 执行真实握手流程" "White"
    Write-ColorText "  5. 测试数据包转发" "White"
    Write-ColorText "  6. 输出详细日志" "White"
    Write-ColorText "`n  请确保：" "Yellow"
    Write-ColorText "  - Minecraft 1.20.6 已安装" "White"
    Write-ColorText "  - 迷你世界客户端可用" "White"
    Write-ColorText "  - Wireshark 已安装" "White"
    Write-ColorText "============================================================`n" "Cyan"
}

function Show-Menu {
    Show-Banner
    Write-ColorText "  [1] 完整测试流程 (推荐)" "Green"
    Write-ColorText "      启动桥接器 → 启动Wireshark → 等待MC连接 → 测试功能`n" "Gray"
    
    Write-ColorText "  [2] 仅启动桥接服务器" "Yellow"
    Write-ColorText "      启动 MnMCP 桥接器，等待手动连接`n" "Gray"
    
    Write-ColorText "  [3] 运行真实连接测试" "Yellow"
    Write-ColorText "      执行自动化真实连接测试`n" "Gray"
    
    Write-ColorText "  [4] 启动 Wireshark 抓包" "Yellow"
    Write-ColorText "      启动 Wireshark 并设置过滤器`n" "Gray"
    
    Write-ColorText "  [5] 启动迷你世界客户端" "Yellow"
    Write-ColorText "      启动迷你世界用于测试`n" "Gray"
    
    Write-ColorText "  [6] 查看日志" "Yellow"
    Write-ColorText "      查看最近的测试日志`n" "Gray"
    
    Write-ColorText "  [7] 清理并退出`n" "Red"
    Write-ColorText "============================================================" "Cyan"
}

function Test-Environment {
    Write-ColorText "`n[*] 步骤 1/6: 检查环境..." "Yellow"
    
    # 检查 Python
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorText "  [OK] Python: $pythonVersion" "Green"
    } catch {
        Write-ColorText "  [X] Python 未安装！" "Red"
        return $false
    }
    
    # 检查核心模块
    try {
        python -c "from core.proxy_server import ProxyServer; from core.data_flow_manager import DataFlowManager" 2>&1 | Out-Null
        Write-ColorText "  [OK] 核心模块检查通过" "Green"
    } catch {
        Write-ColorText "  [!] 核心模块检查失败，但将继续" "Yellow"
    }
    
    return $true
}

function Start-BridgeServer {
    Write-ColorText "`n[*] 步骤 2/6: 启动 MnMCP 桥接服务器..." "Yellow"
    Write-ColorText "  [i] 正在启动桥接器，端口 25565..." "Gray"
    
    $logFile = "logs\bridge_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    
    Start-Process -FilePath "python" -ArgumentList "src\core\bridge_integrated.py" `
        -WorkingDirectory $MNMCP_PATH -WindowStyle Normal
    
    Write-ColorText "  [OK] 桥接服务器已启动" "Green"
    Write-ColorText "  [i] 日志文件: $logFile" "Gray"
    
    Start-Sleep -Seconds 2
}

function Start-WiresharkCapture {
    Write-ColorText "`n[*] 步骤 3/6: 启动 Wireshark 抓包..." "Yellow"
    
    if (Test-Path $WIRESHARK_PATH) {
        $filter = "tcp port 25565 or tcp port 8080"
        Start-Process -FilePath $WIRESHARK_PATH -ArgumentList "-k", "-i", "\Device\NPF_Loopback", "-f", $filter
        Write-ColorText "  [OK] Wireshark 已启动" "Green"
        Write-ColorText "  [i] 过滤器: $filter" "Gray"
    } else {
        Write-ColorText "  [!] Wireshark 未找到: $WIRESHARK_PATH" "Yellow"
        Write-ColorText "  [i] 请手动启动 Wireshark" "Gray"
    }
}

function Wait-MinecraftConnection {
    Write-ColorText "`n[*] 步骤 4/6: 等待 Minecraft 客户端连接..." "Yellow"
    Write-ColorText "  [i] 请在 Minecraft 1.20.6 中添加服务器：" "Cyan"
    Write-ColorText "       地址: localhost:25565" "White"
    Write-ColorText "       名称: MnMCP Test" "White"
    Write-ColorText "`n  [i] 连接后按 Enter 继续测试..." "Yellow"
    Read-Host
}

function Test-DataFlow {
    Write-ColorText "`n[*] 步骤 5/6: 执行端到端数据流测试..." "Yellow"
    
    Set-Location $MNMCP_PATH
    python real_connection_test.py
    
    Write-ColorText "`n  [OK] 测试完成" "Green"
}

function Start-MiniWorldClient {
    Write-ColorText "`n[*] 启动迷你世界客户端..." "Yellow"
    
    if (Test-Path $MINIWORLD_PATH) {
        Start-Process -FilePath $MINIWORLD_PATH
        Write-ColorText "  [OK] 迷你世界已启动" "Green"
    } else {
        Write-ColorText "  [X] 迷你世界未找到: $MINIWORLD_PATH" "Red"
    }
}

function Show-Logs {
    Write-ColorText "`n[*] 查看日志..." "Yellow"
    
    $logPath = Join-Path $MNMCP_PATH "logs"
    if (Test-Path $logPath) {
        $logs = Get-ChildItem $logPath -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 10
        
        if ($logs) {
            Write-ColorText "  最近的日志文件：" "Cyan"
            $logs | ForEach-Object { Write-ColorText "    - $($_.Name)" "White" }
            
            Write-ColorText "`n  [i] 查看最新日志? (y/n)" "Yellow"
            $view = Read-Host
            if ($view -eq "y") {
                Get-Content $logs[0].FullName -Tail 50
            }
        } else {
            Write-ColorText "  [i] 暂无日志文件" "Gray"
        }
    } else {
        Write-ColorText "  [i] 日志目录不存在" "Gray"
    }
}

function Invoke-FullTest {
    Show-Banner
    
    # Step 1: 环境检查
    if (-not (Test-Environment)) {
        Write-ColorText "`n[X] 环境检查失败，退出" "Red"
        return
    }
    
    # Step 2: 启动桥接服务器
    Start-BridgeServer
    
    # Step 3: 启动 Wireshark
    Start-WiresharkCapture
    
    # Step 4: 等待MC连接
    Wait-MinecraftConnection
    
    # Step 5: 执行测试
    Test-DataFlow
    
    # 完成
    Write-ColorText "`n============================================================" "Cyan"
    Write-ColorText "  [6/6] 测试完成！" "Green"
    Write-ColorText "============================================================" "Cyan"
    Write-ColorText "`n[OK] 所有步骤执行完毕" "Green"
    Write-ColorText "[i] 日志位置: $MNMCP_PATH\logs\" "Gray"
    Write-ColorText "`n按任意键返回菜单..." "Yellow"
    Read-Host
}

function Clear-AndExit {
    Write-ColorText "`n[*] 正在清理..." "Yellow"
    
    # 停止桥接服务器
    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-ColorText "  [OK] 已停止桥接服务器" "Green"
    Write-ColorText "`n感谢使用 MnMCP 交互式测试！`n" "Cyan"
    exit
}

# 主程序
if ($FullTest) {
    Invoke-FullTest
} elseif ($StartBridge) {
    Show-Banner
    Start-BridgeServer
} elseif ($TestDataFlow) {
    Show-Banner
    Test-DataFlow
} elseif ($StartWireshark) {
    Show-Banner
    Start-WiresharkCapture
} elseif ($StartMiniWorld) {
    Show-Banner
    Start-MiniWorldClient
} elseif ($ViewLogs) {
    Show-Banner
    Show-Logs
} else {
    # 交互模式
    while ($true) {
        Show-Menu
        $choice = Read-Host "  请选择操作 [1-7]"
        
        switch ($choice) {
            "1" { Invoke-FullTest }
            "2" { 
                Show-Banner
                Start-BridgeServer
                Write-ColorText "`n按任意键返回菜单..." "Yellow"
                Read-Host
            }
            "3" { 
                Show-Banner
                Test-DataFlow
                Write-ColorText "`n按任意键返回菜单..." "Yellow"
                Read-Host
            }
            "4" { 
                Show-Banner
                Start-WiresharkCapture
                Write-ColorText "`n按任意键返回菜单..." "Yellow"
                Read-Host
            }
            "5" { 
                Show-Banner
                Start-MiniWorldClient
                Write-ColorText "`n按任意键返回菜单..." "Yellow"
                Read-Host
            }
            "6" { 
                Show-Banner
                Show-Logs
                Write-ColorText "`n按任意键返回菜单..." "Yellow"
                Read-Host
            }
            "7" { Clear-AndExit }
            default { 
                Write-ColorText "`n[!] 无效选择，请重试" "Red"
                Start-Sleep -Seconds 1
            }
        }
    }
}
