# MnMCP 部署和运行文档

## 快速部署（推荐）

### 1. 下载项目

```bash
git clone https://github.com/starsailsclover/MnMCP.git
cd MnMCP
```

### 2. 运行安装脚本

**Windows:**
```bash
run.bat
```

或

```bash
python setup.py
```

**Linux/macOS:**
```bash
python3 setup.py
```

### 3. 启动服务

```bash
python start.py
```

---

## 详细部署步骤

### 环境准备

#### 安装 Python 3.11+

访问 [python.org](https://python.org/downloads) 下载安装。

**注意**：安装时勾选 "Add Python to PATH"。

#### 验证 Python

```bash
python --version
# 应显示 Python 3.11.x 或更高
```

### 安装依赖

```bash
pip install websockets pyyaml cryptography
```

或使用国内镜像：

```bash
pip install websockets pyyaml cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 验证安装

```bash
python check_project_integrity.py
```

预期输出：
```
Result: 9/9 checks passed
Status: ALL CHECKS PASSED
```

---

## 运行服务

### 基本运行

```bash
python start.py
```

服务启动后：
- MNW监听: `0.0.0.0:8080`
- MC目标: `127.0.0.1:19132`

### 后台运行（Linux）

```bash
nohup python start.py > mnmcp.log 2>&1 &
```

### 使用 systemd（Linux服务器）

创建服务文件 `/etc/systemd/system/mnmcp.service`：

```ini
[Unit]
Description=MnMCP Proxy Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/MnMCP
ExecStart=/usr/bin/python3 start.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable mnmcp
sudo systemctl start mnmcp
```

---

## 配置说明

### 配置文件 `config.yaml`

```yaml
server:
  # MNW监听配置
  mnw_host: "0.0.0.0"
  mnw_port: 8080
  
  # MC服务器配置
  mc_host: "127.0.0.1"
  mc_port: 19132
  
  # 性能配置
  max_clients: 100
  buffer_size: 65536
  timeout: 30.0

# 功能开关
features:
  enable_translation: true
  enable_heartbeat: true
  
# 日志配置
logging:
  level: "INFO"
  console: true
```

### 环境变量

可以通过环境变量覆盖配置：

```bash
export MNW_HOST=0.0.0.0
export MNW_PORT=8080
export MC_HOST=127.0.0.1
export MC_PORT=19132
```

---

## 连接游戏

### Minecraft

1. 打开 Minecraft 启动器
2. 选择版本 1.20.6+
3. 多人游戏 → 添加服务器
4. 地址：`127.0.0.1:19132`
5. 加入服务器

### 迷你世界

1. 打开迷你世界
2. 开始游戏 → 联机大厅
3. 创建房间
4. 高级设置：
   - 服务器：`127.0.0.1`
   - 端口：`8080`
5. 创建

---

## 故障排除

### 服务无法启动

**检查端口占用：**
```bash
# Windows
netstat -ano | findstr :8080

# Linux/macOS
lsof -i :8080
```

**检查依赖：**
```bash
pip list | grep -E "websockets|pyyaml|cryptography"
```

### 连接失败

1. 确认服务已启动
2. 检查防火墙设置
3. 验证配置文件
4. 查看日志输出

### 性能问题

**降低延迟：**
- 使用本地网络
- 优化服务器配置
- 减少并发连接数

---

## 监控和日志

### 查看日志

```bash
# 实时查看
tail -f logs/mnmcp.log

# 查看最后100行
tail -n 100 logs/mnmcp.log
```

### 性能监控

访问 `http://localhost:8081` 查看监控面板。

---

## 更新部署

### 更新代码

```bash
git pull origin main
```

### 更新依赖

```bash
pip install -r requirements.txt --upgrade
```

### 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart mnmcp

# 或直接停止后重新启动
# Ctrl+C 停止，然后 python start.py
```

---

## 安全建议

1. **修改默认端口** - 避免使用默认端口
2. **配置防火墙** - 只开放必要端口
3. **使用HTTPS** - 生产环境启用SSL
4. **定期更新** - 保持代码和依赖更新

---

## 获取帮助

- **文档**: [MnMCP文档中心](https://starsailsclover.github.io/MnMCP-Introducing-Website/MnMCPDocuments/)
- **QQ群**: 1084172731
- **GitHub Issues**: [提交问题](https://github.com/starsailsclover/MnMCP/issues)

---

**部署完成！开始跨平台联机吧！** 🎮
