#!/usr/bin/env python3
"""
准备项目上传GitHub
整理文件结构，创建部署脚本
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_DIR = Path(__file__).parent.resolve()
RESOURCES_DIR = Path(r"https://github.com/StarsailsClover/MnMCPResources")

def clean_project():
    """清理项目，移除不需要的文件"""
    print("[*] 清理项目...")
    
    # 需要删除的文件
    to_remove = [
        "CHECKPOINT_RESUME.md",
        "QUICK_ACTION.md",
        "QUICK_START.md",
        "QUICK_START_DEX.md",
        "SESSION_023_TESTING_COMPLETE.md",
        "VERIFICATION_REPORT.md",
        "FINAL_PROGRESS_REPORT.md",
        "ORGANIZATION_SUMMARY.md",
        "organize_project.py",
        "organize_project_v2.py",
        "move_large_files.py",
        "cleanup_and_prepare.py",
        "check_apk_detailed.py",
        "check_apk_source.py",
        "check_official_apk.py",
        "decompile_both_platforms.py",
        "recompile_official.py",
        "check_and_fix_components.py",
    ]
    
    for filename in to_remove:
        filepath = PROJECT_DIR / filename
        if filepath.exists():
            filepath.unlink()
            print(f"  [-] 删除: {filename}")
    
    print("[+] 清理完成")

def create_requirements():
    """创建requirements.txt"""
    print("\n[*] 创建requirements.txt...")
    
    requirements = """# MnMCP 依赖
# Python 3.11+

# 核心依赖（Python标准库）
# asyncio - 异步IO
# socket - 网络通信
# struct - 二进制数据处理
# json - JSON处理
# hashlib - 哈希计算
# logging - 日志记录

# 测试依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
"""
    
    req_file = PROJECT_DIR / "requirements.txt"
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print(f"  [+] {req_file}")

def create_setup_scripts():
    """创建安装脚本"""
    print("\n[*] 创建安装脚本...")
    
    # Windows PowerShell脚本
    ps1_content = '''# MnMCP 安装脚本 (Windows)
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
& .\\venv\\Scripts\\Activate.ps1

# 安装依赖
Write-Host "[*] 安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 创建配置目录
$configDir = "$env:USERPROFILE\\.mnmcp"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "[*] 创建配置目录: $configDir" -ForegroundColor Green
}

# 复制配置
if (-not (Test-Path "$configDir\\config.json")) {
    Copy-Item "config\\config.example.json" "$configDir\\config.json"
    Write-Host "[*] 创建默认配置" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "启动代理: python start_proxy.py" -ForegroundColor Cyan
Write-Host "运行测试: python -m pytest tests\\" -ForegroundColor Cyan
Write-Host ""
'''
    
    scripts_dir = PROJECT_DIR / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    ps1_file = scripts_dir / "setup.ps1"
    with open(ps1_file, 'w', encoding='utf-8') as f:
        f.write(ps1_content)
    print(f"  [+] {ps1_file}")
    
    # Bash脚本
    sh_content = '''#!/bin/bash
# MnMCP 安装脚本 (Linux/Mac)

echo "========================================"
echo "MnMCP 安装脚本"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "请安装Python 3.11+"
    exit 1
fi

echo "[*] Python版本: $(python3 --version)"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[*] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[*] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[*] 安装依赖..."
pip install -r requirements.txt

# 创建配置目录
CONFIG_DIR="$HOME/.mnmcp"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    echo "[*] 创建配置目录: $CONFIG_DIR"
fi

# 复制配置
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cp config/config.example.json "$CONFIG_DIR/config.json"
    echo "[*] 创建默认配置"
fi

echo ""
echo "========================================"
echo "安装完成!"
echo "========================================"
echo ""
echo "启动代理: python start_proxy.py"
echo "运行测试: python -m pytest tests/"
echo ""
'''
    
    sh_file = scripts_dir / "setup.sh"
    with open(sh_file, 'w', encoding='utf-8') as f:
        f.write(sh_content)
    print(f"  [+] {sh_file}")

def create_config_example():
    """创建示例配置文件"""
    print("\n[*] 创建示例配置...")
    
    config = {
        "proxy": {
            "host": "127.0.0.1",
            "port": 25565,
            "max_connections": 100
        },
        "miniworld": {
            "auth_server": "mwu-api-pre.mini1.cn",
            "auth_port": 443,
            "preferred_cdn": "tencent"
        },
        "account_mapping": {
            "auto_create": True,
            "default_nickname": "MCPlayer"
        },
        "logging": {
            "level": "INFO",
            "file": "~/.mnmcp/proxy.log"
        },
        "performance": {
            "buffer_size": 65536,
            "worker_threads": 4
        }
    }
    
    config_dir = PROJECT_DIR / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.example.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"  [+] {config_file}")

def create_release_script():
    """创建发布脚本"""
    print("\n[*] 创建发布脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""创建Release包"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
RELEASE_DIR = PROJECT_DIR / "releases"

def create_release():
    """创建发布包"""
    version = "1.0.0"
    release_name = f"mnmcp-v{version}"
    release_path = RELEASE_DIR / release_name
    
    print(f"[*] 创建发布包: {release_name}")
    
    # 创建发布目录
    if release_path.exists():
        shutil.rmtree(release_path)
    release_path.mkdir(parents=True)
    
    # 复制必要文件
    files_to_include = [
        "src",
        "tests",
        "tools",
        "docs",
        "config",
        "scripts",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        "LICENSE",
        "requirements.txt",
        "start_proxy.py",
        "test_import.py",
    ]
    
    for item in files_to_include:
        src = PROJECT_DIR / item
        dst = release_path / item
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"  [+] {item}")
    
    # 创建ZIP
    zip_path = RELEASE_DIR / f"{release_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(release_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(release_path)
                zf.write(file_path, arcname)
    
    print(f"[+] 发布包创建完成: {zip_path}")
    print(f"[+] 目录: {release_path}")

if __name__ == "__main__":
    create_release()
'''
    
    scripts_dir = PROJECT_DIR / "scripts"
    release_file = scripts_dir / "create_release.py"
    with open(release_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    print(f"  [+] {release_file}")

def update_gitignore():
    """更新.gitignore"""
    print("\n[*] 更新.gitignore...")
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# 配置和日志
*.log
.mnmcp/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 测试
.pytest_cache/
.coverage

# 发布
releases/

# 大文件（应该在外部资源中）
*.apk
*.exe
*.dll
*.jar
*.pcapng
*.pcap
'''
    
    gitignore_file = PROJECT_DIR / ".gitignore"
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"  [+] {gitignore_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("准备项目上传GitHub")
    print("=" * 60)
    print()
    
    # 执行任务
    clean_project()
    create_requirements()
    create_setup_scripts()
    create_config_example()
    create_release_script()
    update_gitignore()
    
    print("\n" + "=" * 60)
    print("准备完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 检查项目结构")
    print("2. 运行测试: python -m pytest tests/")
    print("3. 创建发布包: python scripts/create_release.py")
    print("4. 提交到GitHub")

if __name__ == "__main__":
    main()
