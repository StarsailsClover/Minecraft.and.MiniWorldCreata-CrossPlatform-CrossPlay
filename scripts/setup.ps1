# MnMCP 安装脚本 (Windows)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MnMCP 安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到Python" -ForegroundColor Red
    Write-Host "请安装Python 3.11+ 从 https://python.org"
    exit 1
}
Write-Host "[*] Python版本: $pythonVersion" -ForegroundColor Green

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "[*] 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "[*] 激活虚拟环境..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "[*] 安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 创建配置目录
$configDir = "$env:USERPROFILE\.mnmcp"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "[*] 创建配置目录: $configDir" -ForegroundColor Green
}

# 复制配置
if (-not (Test-Path "$configDir\config.json")) {
    Copy-Item "config\config.example.json" "$configDir\config.json"
    Write-Host "[*] 创建默认配置" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "启动代理: python start_proxy.py" -ForegroundColor Cyan
Write-Host "运行测试: python -m pytest tests\" -ForegroundColor Cyan
Write-Host ""
