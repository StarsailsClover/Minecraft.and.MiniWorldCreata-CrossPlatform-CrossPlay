# MnMCP 用户使用指南

**版本**: v0.6.0  
**更新日期**: 2026-02-28

---

## 快速开始

### 1. 安装依赖

打开命令提示符(CMD)或PowerShell，运行：

```bash
pip install websockets pyyaml cryptography
```

或者使用自动安装脚本：

```bash
python start_v2.py
```

### 2. 启动代理服务器

```bash
python start_v2.py
```

你会看到类似输出：
```
╔════════════════════════════════════════════════════════════════════╗
║               MnMCP 智能启动器 v2                                  ║
║          Minecraft ↔ MiniWorld 跨平台联机                       ║
╚════════════════════════════════════════════════════════════════════╝

[✓] Python版本: 3.11.0

[1/4] 检查依赖...
  [✓] websockets>=12.0 已安装
  [✓] pyyaml>=6.0 已安装
  [✓] cryptography>=41.0.0 已安装

[2/4] 检查项目文件...
  [✓] 配置文件: config.yaml
  [✓] 方块映射: data/mnw_block_mapping_from_go.json
  [✓] 启动脚本: start.py

[3/4] 运行测试...
  [✓] 加密模块: 通过
  [✓] 方块映射: 通过
  [✓] 协议翻译: 通过

[4/4] 启动服务器...
  服务器配置:
    MNW监听: 0.0.0.0:8080
    MC目标: 127.0.0.1:19132
    最大客户端: 100

  正在启动代理服务器...
  [✓] 代理服务器已启动
```

### 3. 启动Minecraft

1. 打开Minecraft启动器
2. 选择版本（推荐1.20.6）
3. 点击"多人游戏"
4. 点击"添加服务器"
5. 服务器地址输入: `127.0.0.1:19132`
6. 点击"加入服务器"

### 4. 启动迷你世界

1. 打开迷你世界
2. 点击"开始游戏"
3. 选择"联机大厅"
4. 点击"创建房间"
5. 在高级设置中，服务器地址输入: `127.0.0.1:8080`
6. 点击"创建"

### 5. 开始联机！

现在你可以在Minecraft和迷你世界之间：
- ✅ 看到对方的玩家
- ✅ 聊天消息互通
- ✅ 方块同步（放置/破坏）
- ✅ 位置同步

---

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
  enable_heartbeat: true      # 启用心跳
  
# 日志配置
logging:
  level: "INFO"              # 日志级别: DEBUG, INFO, WARNING, ERROR
  console: true              # 输出到控制台
```

### 自定义配置

创建自己的配置文件 `myconfig.yaml`：

```yaml
server:
  mnw_host: "0.0.0.0"
  mnw_port: 8080
  mc_host: "127.0.0.1"
  mc_port: 19132
  max_clients: 50

features:
  enable_translation: true
  enable_compression: false
```

启动时使用：
```bash
python start_v2.py --config myconfig.yaml
```

---

## 故障排除

### 问题1: 依赖安装失败

**现象**: `pip install` 命令失败

**解决**:
```bash
# 更新pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install websockets pyyaml cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: 端口被占用

**现象**: `Address already in use`

**解决**:
1. 查找占用端口的程序：
```bash
netstat -ano | findstr :8080
```

2. 修改配置文件使用其他端口：
```yaml
server:
  mnw_port: 8081  # 改为其他端口
```

### 问题3: 无法连接到服务器

**现象**: 游戏显示"连接失败"

**检查清单**:
- [ ] 代理服务器是否已启动
- [ ] 防火墙是否允许端口
- [ ] 游戏客户端地址是否正确
- [ ] 配置文件中的端口是否匹配

### 问题4: 方块不同步

**现象**: 放置的方块对方看不到

**解决**:
1. 检查方块是否在映射表中
2. 查看日志是否有错误
3. 尝试重新连接

---

## 高级功能

### 性能监控

启动后访问监控界面：
```
http://localhost:8081
```

### 日志查看

日志文件位置：`logs/mnmcp.log`

实时查看日志：
```bash
tail -f logs/mnmcp.log
```

### 加密配置

加密敏感配置：
```bash
python tools/encrypt_config.py config.yaml
```

解密配置：
```bash
python tools/decrypt_config.py
```

---

## 常见问题 (FAQ)

### Q: 支持哪些版本的Minecraft？

A: 目前测试支持：
- Minecraft Java 1.20.6
- Minecraft Bedrock 1.20.x

### Q: 支持哪些版本的迷你世界？

A: 支持：
- 迷你世界国服 PC版 1.53.1
- 迷你世界外服 PC版
- 迷你世界手游版

### Q: 最多支持多少玩家？

A: 默认配置支持100个并发连接，可通过配置调整。

### Q: 延迟是多少？

A: 本地测试延迟通常在10-50ms之间，取决于网络环境。

### Q: 是否支持Mod？

A: 基础方块支持，Mod方块需要添加到映射表。

---

## 获取帮助

### 项目地址
- GitHub: [项目链接]
- 官网: https://starsailsclover.github.io/MnMCP-Introducing-Website/

### 社区
- QQ群: 1084172731
- Discord: [邀请链接]

### 问题反馈
- GitHub Issues: [链接]
- 邮箱: SailsHuang@gmail.com

---

## 更新日志

### v0.6.0 (2026-02-28)
- ✨ 智能启动脚本
- ✨ 自动依赖安装
- ✨ 性能监控
- ✨ 错误处理

### v0.5.0 (2026-02-28)
- ✨ 性能监控模块
- ✨ 错误处理模块
- ✨ 项目完整性检查

### v0.4.0 (2026-02-28)
- ✨ Minecraft协议支持
- ✨ 代理服务器v2
- ✨ 配置系统

---

**祝联机愉快！** 🎮
