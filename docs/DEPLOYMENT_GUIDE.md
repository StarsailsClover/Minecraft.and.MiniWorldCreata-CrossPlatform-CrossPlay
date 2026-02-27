# MnMCP 部署指南

本文档提供 MnMCP 项目的完整部署说明，包括一键部署和手动部署两种方式。

---

## 📋 部署前准备

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 20GB SSD | 50GB+ SSD |
| 网络 | 10Mbps | 100Mbps+ |

### 软件依赖

- Python 3.11+
- Java 17+ (用于 PaperMC)
- Git
- Nginx (可选，用于反向代理)

---

## 🚀 一键部署（推荐）

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay

# 2. 运行一键部署脚本
python deploy.py --mode=full

# 3. 按照提示输入配置信息
# 脚本会自动解密配置文件并启动服务
```

### 部署模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `minimal` | 仅部署核心代理服务 | 开发测试 |
| `standard` | 部署代理 + PaperMC | 小型服务器 |
| `full` | 完整部署（代理 + PaperMC + Geyser + Web） | 生产环境 |

---

## 🔧 手动部署

### 步骤1: 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 验证安装
python check_and_fix_components.py
```

### 步骤2: 解密配置文件

```bash
# 使用解密脚本
python tools/decrypt_config.py

# 输入解密密码（从项目维护者获取）
# 解密后的配置将保存到 config/config.json
```

### 步骤3: 配置服务

编辑 `config/config.json`：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 25565,
    "max_players": 100
  },
  "miniworld": {
    "auth_server": "mwu-api-pre.mini1.cn",
    "game_servers": [
      "183.60.230.67:4000",
      "125.88.253.199:4000"
    ]
  },
  "minecraft": {
    "version": "1.20.6",
    "server_type": "paper"
  },
  "geyser": {
    "enabled": true,
    "port": 19132
  }
}
```

### 步骤4: 启动服务

```bash
# 启动代理服务器
python -m src.core.proxy_server

# 或者使用启动脚本
./scripts/start_server.sh
```

---

## 📦 外部资源库

项目依赖外部资源库 `MnMCPResources/`，包含：

- APK文件和反编译结果
- DEX分析数据
- 抓包捕获文件
- 历史备份

### 获取资源库

```bash
# 方式1: 从项目维护者获取
# 联系项目维护者获取 MnMCPResources 访问权限

# 方式2: 自行准备（高级用户）
# 按照 docs/RESOURCE_PREPARATION.md 准备资源
```

---

## 🔐 安全配置

### 敏感信息加密

项目中敏感信息（API密钥、服务器地址等）已加密存储：

- 加密文件: `config/encrypted/`
- 解密工具: `tools/decrypt_config.py`
- 密钥管理: 联系项目维护者获取解密密钥

### 生产环境建议

1. **使用防火墙** - 仅开放必要端口
2. **配置SSL/TLS** - 使用 HTTPS/WSS
3. **定期备份** - 配置自动备份脚本
4. **监控告警** - 部署监控和日志系统

---

## 🌐 Web管理界面

部署完成后，访问 Web 管理界面：

```
http://localhost:8080/admin
```

默认账号密码：
- 用户名: `admin`
- 密码: （首次启动时自动生成，查看日志获取）

---

## 🐛 故障排除

### 常见问题

#### 1. 解密失败
```
Error: Decryption failed
```
**解决**: 确认解密密钥正确，联系项目维护者

#### 2. 端口被占用
```
Error: Address already in use
```
**解决**: 修改配置文件中的端口，或停止占用端口的程序

#### 3. 资源库缺失
```
Error: MnMCPResources not found
```
**解决**: 联系项目维护者获取资源库，或按照指南自行准备

---

## 📞 技术支持

部署遇到问题？

1. 查看 [故障排除](#故障排除) 章节
2. 搜索 [GitHub Issues](https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/issues)
3. 创建新的 Issue 并提供：
   - 操作系统版本
   - Python版本
   - 错误日志
   - 已尝试的解决方案

---

## 📄 相关文档

- [快速开始](README.md)
- [开发指南](CONTRIBUTING.md)
- [架构文档](docs/TechnicalDocument.md)
- [API文档](docs/API.md)