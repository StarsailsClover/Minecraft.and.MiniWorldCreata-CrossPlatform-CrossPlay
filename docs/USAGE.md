# MnMCP 使用指南

## 目录

- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [运行模式](#运行模式)
- [故障排除](#故障排除)
- [高级用法](#高级用法)

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.11+
- Minecraft Java版 1.20.6
- 迷你世界 PC版 1.53.1

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动

```bash
# 启动代理服务器
python run_proxy.py
```

### 4. 连接

1. 打开 Minecraft 1.20.6
2. 多人游戏 → 添加服务器
3. 服务器地址: `localhost:25565`
4. 连接服务器

## 配置说明

### 基础配置

编辑 `config.json`:

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
    "version": "1.20.6",
    "protocol_version": 766
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mnmcp.log"
  }
}
```

### 配置项说明

#### 服务器配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| host | string | "0.0.0.0" | 监听地址 |
| port | int | 25565 | 监听端口 |
| max_connections | int | 100 | 最大连接数 |

#### 迷你世界配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| version | string | "1.53.1" | 游戏版本 |
| region | string | "CN" | 区域 (CN/GLOBAL) |
| auth_host | string | "mwu-api-pre.mini1.cn" | 认证服务器 |

#### Minecraft配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| version | string | "1.20.6" | 游戏版本 |
| protocol_version | int | 766 | 协议版本 |

## 运行模式

### 1. 标准模式

```bash
python run_proxy.py
```

### 2. 调试模式

```bash
python run_proxy.py --debug
```

### 3. 自定义配置

```bash
python run_proxy.py --config my_config.json
```

### 4. 指定端口

```bash
python run_proxy.py --port 25566
```

## 故障排除

### 问题1: 端口被占用

**症状**: 
```
[Errno 10048] error while attempting to bind on address ('0.0.0.0', 25565)
```

**解决**:
```bash
# Windows
netstat -ano | findstr :25565
taskkill /PID <PID> /F

# 或使用其他端口
python run_proxy.py --port 25566
```

### 问题2: 连接超时

**症状**: 
```
Connection timeout
```

**解决**:
1. 检查防火墙设置
2. 确认代理服务器已启动
3. 检查网络连接

### 问题3: 协议错误

**症状**: 
```
Protocol error: Invalid packet
```

**解决**:
1. 确认Minecraft版本为1.20.6
2. 检查日志文件 `logs/mnmcp.log`
3. 启用调试模式查看详细日志

### 问题4: 方块不同步

**症状**: 放置的方块显示不正确

**解决**:
1. 检查 `data/block_mappings.json` 是否完整
2. 确认方块ID映射正确
3. 查看日志中的方块转换信息

## 高级用法

### 数据包捕获

```bash
# 启动数据包捕获
python packet_capture.py

# 捕获的数据保存在 captures/ 目录
# 格式: JSON Lines
```

### 网络监控

```bash
# 启动网络监控
python network_monitor.py

# 实时显示数据包信息
```

### 性能测试

```bash
# 运行性能测试
python test_complete_flow.py

# 查看性能指标
```

### 自定义方块映射

编辑 `data/block_mappings.json`:

```json
{
  "mappings": [
    {
      "mc_id": 1,
      "mc_name": "石头",
      "mnw_id": 1,
      "mnw_name": "stone",
      "verified": true
    }
  ]
}
```

### 日志级别设置

在 `config.json` 中设置:

```json
{
  "logging": {
    "level": "DEBUG",  // DEBUG, INFO, WARNING, ERROR
    "file": "logs/mnmcp.log"
  }
}
```

## 常见问题

### Q: 支持哪些Minecraft版本?

A: 目前支持 Minecraft Java版 1.20.6

### Q: 支持迷你世界外服吗?

A: 基础架构已支持，需要进一步测试

### Q: 可以同时连接多个玩家吗?

A: 支持，默认最大100个并发连接

### Q: 数据包会被保存吗?

A: 可以，使用 `packet_capture.py` 启用捕获

### Q: 如何查看日志?

A: 日志文件位于 `logs/mnmcp.log`

## 更新日志

### v0.1.0 (2026-02-27)

- 初始版本发布
- 支持基础联机功能
- 实现协议翻译
- 支持48个方块映射

## 获取帮助

- 查看 [API文档](API.md)
- 查看 [协议分析](PROTOCOL.md)
- 提交 [Issue](https://github.com/StarsailsClover/MnMCP/issues)
