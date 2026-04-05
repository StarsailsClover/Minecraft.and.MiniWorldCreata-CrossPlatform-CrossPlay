# 安装部署指南

## 系统要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.11 或更高版本
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 500MB 可用空间

## 快速安装

### 方法一：使用安装脚本（推荐）

1. 下载项目到本地
2. 在项目目录下打开命令行
3. 运行安装脚本：

```bash
python setup.py
```

脚本会自动：
- 检查Python版本
- 安装必要的依赖
- 验证项目完整性
- 启动服务（可选）

### 方法二：手动安装

#### 1. 安装Python

如果尚未安装Python，请访问 [python.org](https://python.org) 下载并安装 Python 3.11+。

**注意**：安装时请勾选 "Add Python to PATH"。

#### 2. 安装依赖

```bash
pip install websockets pyyaml cryptography
```

或使用国内镜像加速：

```bash
pip install websockets pyyaml cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 验证安装

```bash
python check_project_integrity.py
```

预期输出：
```
Result: 9/9 checks passed
Status: ALL CHECKS PASSED
```

## 部署方式

### 本地部署

适用于个人测试和开发：

```bash
python start.py
```

服务将启动在：
- MNW监听: `0.0.0.0:8080`
- MC目标: `127.0.0.1:19132`

### 服务器部署

适用于生产环境：

1. 编辑 `config.yaml` 配置：

```yaml
server:
  mnw_host: "0.0.0.0"
  mnw_port: 8080
  mc_host: "your-mc-server-ip"
  mc_port: 19132
  max_clients: 100
```

2. 使用进程管理器（如pm2、systemd）保持服务运行

3. 配置防火墙允许端口访问

## 目录结构

```
MnMCP/
├── run.bat              # Windows启动脚本
├── start.py             # Python启动脚本
├── setup.py             # 安装脚本
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖列表
├── src/                 # 源代码
│   ├── core/           # 核心模块
│   ├── crypto/         # 加密模块
│   ├── protocol/       # 协议模块
│   └── utils/          # 工具模块
├── tests/              # 测试文件
├── data/               # 数据文件
└── docs/               # 文档
```

## 常见问题

### Q: 安装依赖时速度慢？

A: 使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 端口被占用？

A: 编辑 `config.yaml` 修改端口号：
```yaml
server:
  mnw_port: 8081  # 修改为其他端口
```

### Q: Python版本不兼容？

A: 确保安装 Python 3.11+。可以使用 `install_python.py` 自动安装。

## 下一步

安装完成后，请参阅 [使用指南](usage.html) 了解如何启动服务并连接游戏。
