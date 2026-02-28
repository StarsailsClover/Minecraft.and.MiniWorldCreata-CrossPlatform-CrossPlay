<!-- 
此文档已脱敏处理
处理时间: 2026-02-28T13:37:25.564992
原始文件: DEPLOYMENT_GUIDE.md
-->

# MnMCP 部署指南

**版本**: 1.0  
**日期**: 2026-02-26

---

## 1. 系统要求

### 1.1 最低配置
- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.11+
- **内存**: 4 GB RAM
- **网络**: 稳定的互联网连接

### 1.2 推荐配置
- **操作系统**: Windows 11 / Ubuntu 22.04
- **Python**: 3.11+
- **内存**: 8 GB RAM
- **网络**: 100Mbps+ 宽带

---

## 2. 安装步骤

### 2.1 克隆仓库

```bash
git clone https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
```

### 2.2 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.3 配置环境

```bash
# 创建配置目录
mkdir -p ~/.mnmcp

# 复制配置文件
cp config/config.example.json ~/.mnmcp/config.json

# 编辑配置
nano ~/.mnmcp/config.json
```

---

## 3. 配置说明

### 3.1 基本配置

编辑 `~/.mnmcp/config.json`:

```json
{
  "proxy": {
    "host": "127.0.0.1",
    "port": 25565,
    "max_connections": 100
  },
  "miniworld": {
    "auth_server": "[数据处理字符:20]",
    "auth_port": 443,
    "preferred_cdn": "tencent"
  },
  "account_mapping": {
    "auto_create": true,
    "default_nickname": "MCPlayer"
  },
  "logging": {
    "level": "INFO",
    "file": "~/.mnmcp/proxy.log"
  }
}
```

### 3.2 账户映射

创建账户映射文件 `~/.mnmcp/account_mappings.json`:

```json
{
  "minecraft_uuid_1": "miniworld_account_id_1",
  "minecraft_uuid_2": "miniworld_account_id_2"
}
```

### 3.3 方块映射

创建方块映射文件 `~/.mnmcp/block_mapping.json`:

```json
{
  "1": 1,
  "2": 2,
  "3": 3
}
```

---

## 4. 运行代理

### 4.1 启动代理服务器

```bash
# 使用启动脚本
python start_proxy.py

# 或者直接运行
python -m src.core.proxy_server
```

### 4.2 验证运行

```bash
# 检查端口监听
netstat -an | grep 25565

# 查看日志
tail -f ~/.mnmcp/proxy.log
```

### 4.3 连接测试

1. 启动Minecraft客户端
2. 添加服务器: `[数据处理字符:15]`
3. 连接服务器
4. 查看代理日志确认连接

---

## 5. 使用指南

### 5.1 首次使用

1. **启动代理**
   ```bash
   python start_proxy.py
   ```

2. **配置Minecraft**
   - 打开Minecraft
   - 多人游戏 -> 添加服务器
   - 服务器地址: `[数据处理字符:15]`
   - 保存并连接

3. **登录迷你世界**
   - 首次连接需要输入迷你号
   - 代理会自动创建账户映射
   - 后续连接自动使用映射

### 5.2 日常使用

```bash
# 1. 启动代理
python start_proxy.py

# 2. 启动Minecraft并连接 [数据处理字符:15]

# 3. 开始游戏
```

### 5.3 停止代理

```bash
# 按 Ctrl+C 停止代理
# 或关闭终端窗口
```

---

## 6. 故障排除

### 6.1 常见问题

#### 问题1: 端口被占用
```
Error: Address already in use
```
**解决**:
```bash
# 查找占用进程
netstat -ano | findstr 25565

# 结束进程
taskkill /PID <PID> /F

# 或更改端口
# 编辑 config.json 修改 port
```

#### 问题2: 连接超时
```
Error: Connection timeout
```
**解决**:
- 检查网络连接
- 检查防火墙设置
- 确认迷你世界服务器状态

#### 问题3: 登录失败
```
Error: Login failed
```
**解决**:
- 检查账户映射配置
- 确认迷你号正确
- 查看日志获取详细错误

### 6.2 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python start_proxy.py

# 或使用调试工具
python tools/debug/packet_inspector.py
```

### 6.3 日志分析

```bash
# 查看实时日志
tail -f ~/.mnmcp/proxy.log

# 搜索错误
grep ERROR ~/.mnmcp/proxy.log

# 统计连接数
grep "新连接" ~/.mnmcp/proxy.log | wc -l
```

---

## 7. 高级配置

### 7.1 性能优化

编辑 `~/.mnmcp/config.json`:

```json
{
  "performance": {
    "buffer_size": 65536,
    "max_connections": 200,
    "worker_threads": 4,
    "enable_compression": true
  }
}
```

### 7.2 安全设置

```json
{
  "security": {
    "enable_encryption": true,
    "max_login_attempts": 3,
    "session_timeout": 3600
  }
}
```

### 7.3 负载均衡

```json
{
  "load_balance": {
    "strategy": "round_robin",
    "health_check": true,
    "failover": true
  }
}
```

---

## 8. 测试验证

### 8.1 运行测试

```bash
# 单元测试
python tests/test_protocol.py

# 集成测试
python tests/test_integration.py

# 性能测试
python tests/test_performance.py

# 全部测试
python -m pytest tests/
```

### 8.2 性能基准

```bash
# 测试协议转换性能
python tests/test_performance.py

# 期望结果:
# - 协议转换: >10,000 ops/s
# - 坐标转换: <1 μs
# - 方块映射: <1 μs
```

---

## 9. 更新维护

### 9.1 更新代码

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启代理
# (停止后重新启动)
```

### 9.2 备份配置

```bash
# 备份配置
cp -r ~/.mnmcp ~/.mnmcp.backup

# 恢复配置
cp -r ~/.mnmcp.backup ~/.mnmcp
```

### 9.3 清理日志

```bash
# 清空日志
> ~/.mnmcp/proxy.log

# 或删除旧日志
rm ~/.mnmcp/proxy.log.*
```

---

## 10. 获取帮助

### 10.1 文档
- README.md - 项目介绍
- ProtocolAnalysisReport.md - 协议分析
- TechnicalDocument.md - 技术文档

### 10.2 调试
```bash
# 检查导入
python test_import.py

# 检查配置
python -c "import json; print(json.load(open('~/.mnmcp/config.json')))"

# 测试连接
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 25565)); print('OK')"
```

### 10.3 报告问题

提交Issue时请包含:
1. 操作系统版本
2. Python版本
3. 错误日志
4. 复现步骤

---

## 附录

### A. 目录结构

```
~/.mnmcp/
├── config.json              # 主配置
├── account_mappings.json    # 账户映射
├── block_mapping.json       # 方块映射
├── proxy.log               # 运行日志
└── sessions/               # 会话数据
```

### B. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LOG_LEVEL | 日志级别 | INFO |
| PROXY_HOST | 代理主机 | 127.0.0.1 |
| PROXY_PORT | 代理端口 | 25565 |
| CONFIG_PATH | 配置路径 | ~/.mnmcp/config.json |

### C. 快捷命令

```bash
# 启动
alias mnmcp-start='python start_proxy.py'

# 停止
alias mnmcp-stop='pkill -f proxy_server'

# 查看日志
alias mnmcp-logs='tail -f ~/.mnmcp/proxy.log'

# 测试
alias mnmcp-test='python tests/test_protocol.py'
```

---

**部署指南版本**: 1.0  
**最后更新**: 2026-02-26
