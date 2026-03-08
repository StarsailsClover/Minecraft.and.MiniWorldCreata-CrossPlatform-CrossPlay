# 使用指南

## 启动服务

### Windows

双击运行 `run.bat`，或在命令行中执行：

```bash
python start.py
```

### Linux/macOS

```bash
python3 start.py
```

## 连接游戏

### 1. 启动代理服务

运行启动命令后，您将看到：

```
============================================================
MnMCP - Minecraft & MiniWorld Cross-Platform
============================================================

[INFO] Python 3.11.9
[OK] Python version OK

Server Configuration:
  MNW Listen: 0.0.0.0:8080
  MC Target: 127.0.0.1:19132

Starting MnMCP Proxy Server...
[OK] Proxy server started
```

### 2. 启动 Minecraft

1. 打开 Minecraft 启动器
2. 选择版本 **1.20.6**（推荐）
3. 点击"多人游戏"
4. 点击"添加服务器"
5. 服务器地址填写：`127.0.0.1:19132`
6. 点击"加入服务器"

### 3. 启动迷你世界

1. 打开迷你世界客户端
2. 点击"开始游戏"
3. 选择"联机大厅"
4. 点击"创建房间"
5. 在高级设置中：
   - 服务器地址：`127.0.0.1`
   - 端口：`8080`
6. 点击"创建"

### 4. 开始联机！

现在两个游戏的玩家可以：
- ✅ 看到对方
- ✅ 聊天交流
- ✅ 同步方块（放置/破坏）
- ✅ 位置同步

## 功能演示

运行演示脚本查看已实现功能：

```bash
python demo_connection.py
```

演示内容包括：
- 方块同步
- 玩家移动同步
- 聊天消息转发
- 加密通信
- 方块ID映射

## 配置说明

### 配置文件 `config.yaml`

```yaml
server:
  # MNW监听地址（迷你世界连接到这里）
  mnw_host: "0.0.0.0"
  mnw_port: 8080
  
  # MC服务器地址（Minecraft连接到这里）
  mc_host: "127.0.0.1"
  mc_port: 19132

# 功能开关
features:
  enable_translation: true    # 启用协议翻译
  enable_heartbeat: true      # 启用心跳检测
  
# 日志配置
logging:
  level: "INFO"              # 日志级别
  console: true              # 输出到控制台
```

## 验证运行

### 检查项目完整性

```bash
python check_project_integrity.py
```

### 查看运行状态

服务启动后会显示：
- 连接数
- 数据包统计
- 错误日志

按 `Ctrl+C` 停止服务。

## 故障排除

### 无法连接到代理

1. 检查服务是否已启动
2. 检查防火墙设置
3. 确认端口未被占用

### 方块不同步

1. 检查方块是否在映射表中
2. 查看日志是否有错误
3. 尝试重新连接

### 延迟过高

1. 检查网络连接
2. 确认服务器性能
3. 调整配置参数

## 高级用法

### 自定义方块映射

编辑 `data/mnw_block_mapping_from_go.json` 添加自定义映射。

### 开发插件

参考 `docs/dev/api.html` 了解如何开发自定义插件。

## 获取帮助

- **QQ群**: 1084172731
- **GitHub Issues**: [提交问题](https://github.com/starsailsclover/MnMCP/issues)
- **邮箱**: SailsHuang@gmail.com

## 下一步

- 了解 [架构设计](../dev/architecture.html)
- 查看 [API文档](../dev/api.html)
- 参与项目开发
