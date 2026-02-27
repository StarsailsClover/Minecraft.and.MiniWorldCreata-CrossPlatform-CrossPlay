# MnMCP 部署指南

## 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置](#配置)
- [启动](#启动)
- [监控](#监控)
- [故障排除](#故障排除)

## 系统要求

### 最低配置

- **CPU**: 2核
- **内存**: 2GB RAM
- **磁盘**: 100MB 可用空间
- **网络**: 100Mbps 带宽
- **操作系统**: Windows 10/11, Ubuntu 20.04+, CentOS 8+

### 推荐配置

- **CPU**: 4核+
- **内存**: 4GB RAM+
- **磁盘**: 500MB 可用空间
- **网络**: 1Gbps 带宽
- **操作系统**: Windows Server 2019, Ubuntu 22.04 LTS

## 安装步骤

### 1. 安装 Python

#### Windows

1. 下载 Python 3.11+ 从 [python.org](https://www.python.org/downloads/)
2. 运行安装程序
3. 勾选 "Add Python to PATH"
4. 点击 "Install Now"

验证安装:
```bash
python --version
# Python 3.11.x
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip

# CentOS/RHEL
sudo yum install python311 python311-pip

# 验证
python3.11 --version
```

### 2. 克隆项目

```bash
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP
```

### 3. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

生产环境建议安装 cryptography:
```bash
pip install cryptography
```

### 5. 配置文件

复制默认配置:
```bash
cp config.json.example config.json
```

编辑配置:
```bash
# Windows
notepad config.json

# Linux
nano config.json
```

## 配置

### 基础配置

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 25565,
    "max_connections": 100
  },
  "miniworld": {
    "version": "1.53.1",
    "region": "CN"
  },
  "minecraft": {
    "version": "1.20.6"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mnmcp.log"
  }
}
```

### 生产环境配置

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 25565,
    "max_connections": 500,
    "connection_timeout": 30
  },
  "miniworld": {
    "version": "1.53.1",
    "region": "CN",
    "auth_host": "mwu-api.mini1.cn",
    "game_servers": [
      {"ip": "183.60.230.67", "port": 8080},
      {"ip": "183.36.42.103", "port": 8080}
    ]
  },
  "minecraft": {
    "version": "1.20.6",
    "protocol_version": 766
  },
  "logging": {
    "level": "WARNING",
    "file": "/var/log/mnmcp/mnmcp.log",
    "max_size": "100MB",
    "backup_count": 10
  },
  "security": {
    "encryption_enabled": true,
    "session_timeout": 3600
  },
  "features": {
    "auto_reconnect": true,
    "compression": true,
    "keep_alive": true
  }
}
```

## 启动

### 前台启动（测试）

```bash
python run_proxy.py
```

### 后台启动（生产环境）

#### Windows

使用 NSSM (Non-Sucking Service Manager):

```bash
# 下载 NSSM
# https://nssm.cc/download

# 安装服务
nssm install MnMCP

# 配置
Path: C:\Python311\python.exe
Startup directory: C:\MnMCP
Arguments: run_proxy.py

# 启动服务
nssm start MnMCP
```

#### Linux

使用 systemd:

创建服务文件:
```bash
sudo nano /etc/systemd/system/mnmcp.service
```

内容:
```ini
[Unit]
Description=MnMCP Proxy Server
After=network.target

[Service]
Type=simple
User=mnmcp
WorkingDirectory=/opt/mnmcp
ExecStart=/opt/mnmcp/venv/bin/python run_proxy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
# 创建用户
sudo useradd -r -s /bin/false mnmcp

# 设置权限
sudo chown -R mnmcp:mnmcp /opt/mnmcp

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start mnmcp

# 开机自启
sudo systemctl enable mnmcp

# 查看状态
sudo systemctl status mnmcp
```

### Docker 部署

创建 Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 25565

CMD ["python", "run_proxy.py"]
```

构建和运行:
```bash
# 构建镜像
docker build -t mnmcp:latest .

# 运行容器
docker run -d \
  --name mnmcp \
  -p 25565:25565 \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  mnmcp:latest

# 查看日志
docker logs -f mnmcp
```

## 监控

### 日志监控

```bash
# 实时查看日志
tail -f logs/mnmcp.log

# Windows
Get-Content logs/mnmcp.log -Wait
```

### 性能监控

```bash
# 查看系统资源
top -p $(pgrep -f "python run_proxy.py")

# Windows
Get-Process python | Select-Object CPU, WorkingSet, ProcessName
```

### 网络监控

```bash
# 查看端口监听
netstat -tlnp | grep 25565

# Windows
netstat -ano | findstr :25565
```

### 健康检查

创建健康检查脚本:
```bash
#!/bin/bash
# health_check.sh

if nc -z localhost 25565; then
    echo "MnMCP is running"
    exit 0
else
    echo "MnMCP is not running"
    exit 1
fi
```

## 故障排除

### 端口被占用

```bash
# 查找占用端口的进程
sudo lsof -i :25565

# 结束进程
sudo kill -9 <PID>
```

### 内存不足

```bash
# 查看内存使用
free -h

# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 连接数过多

修改系统限制:
```bash
# 编辑 limits.conf
sudo nano /etc/security/limits.conf

# 添加
mnmcp soft nofile 65536
mnmcp hard nofile 65536

# 编辑 sysctl.conf
sudo nano /etc/sysctl.conf

# 添加
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# 应用
sudo sysctl -p
```

### 防火墙设置

#### Windows

```powershell
# 添加入站规则
New-NetFirewallRule -DisplayName "MnMCP" -Direction Inbound -LocalPort 25565 -Protocol TCP -Action Allow
```

#### Linux

```bash
# UFW
sudo ufw allow 25565/tcp

# firewalld
sudo firewall-cmd --permanent --add-port=25565/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 25565 -j ACCEPT
sudo iptables-save
```

## 备份

### 配置文件备份

```bash
# 创建备份目录
mkdir -p backups

# 备份配置
cp config.json backups/config.json.$(date +%Y%m%d)

# 备份数据
cp -r data backups/data.$(date +%Y%m%d)
```

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/mnmcp"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/mnmcp_$DATE.tar.gz \
    config.json \
    data/ \
    logs/

# 保留最近30天的备份
find $BACKUP_DIR -name "mnmcp_*.tar.gz" -mtime +30 -delete
```

## 更新

### 平滑更新

```bash
# 1. 备份
./backup.sh

# 2. 拉取更新
git pull origin main

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 重启服务
sudo systemctl restart mnmcp
```

### 回滚

```bash
# 恢复配置
cp backups/config.json.20240227 config.json

# 重启服务
sudo systemctl restart mnmcp
```

## 安全建议

1. **使用防火墙** - 只开放必要的端口
2. **定期更新** - 保持系统和依赖更新
3. **日志审计** - 定期检查日志文件
4. **访问控制** - 限制服务器访问权限
5. **数据加密** - 使用 HTTPS/WSS 传输敏感数据
6. **备份策略** - 定期备份配置和数据

## 性能优化

### 系统优化

```bash
# 禁用 IPv6（如果不需要）
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1

# 优化 TCP
echo 'net.ipv4.tcp_tw_reuse = 1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_tw_recycle = 1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 应用优化

1. 调整 `max_connections` 配置
2. 启用 `compression`
3. 调整日志级别为 `WARNING`
4. 使用 SSD 存储日志

## 更多信息

- [使用指南](USAGE.md)
- [API文档](API.md)
- [故障排除](TROUBLESHOOTING.md)
