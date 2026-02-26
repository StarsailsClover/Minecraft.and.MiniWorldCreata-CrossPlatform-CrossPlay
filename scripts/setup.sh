#!/bin/bash
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
