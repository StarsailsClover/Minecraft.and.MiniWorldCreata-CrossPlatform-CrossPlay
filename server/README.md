# Minecraft Java 服务端环境

本目录包含 Minecraft Java 版 1.20.6 服务端及互通模组。

## 目录结构

```
server/
├── paper/                  # PaperMC 服务端
│   ├── paper-1.20.6-151.jar
│   └── paper.jar          # 软链接/副本
├── plugins/               # Paper/Spigot 插件
│   ├── Geyser-Spigot.jar  # Java ↔ Bedrock 桥接
│   └── floodgate-spigot.jar # 基岩版玩家认证
├── fabric/                # Fabric 模组加载器
│   └── fabric-installer.jar
├── mods/                  # Fabric 模组
│   └── fabric-api-0.98.0.jar
├── config/                # 配置文件
└── README.md             # 本文件
```

## 已安装组件

### 1. PaperMC 服务端
- **版本**: 1.20.6 Build 151
- **文件**: `paper/paper-1.20.6-151.jar`
- **用途**: 高性能 Minecraft 服务端
- **启动命令**:
  ```bash
  java -Xmx2G -jar paper.jar nogui
  ```

### 2. GeyserMC
- **文件**: `plugins/Geyser-Spigot.jar`
- **用途**: Java版与基岩版互通桥接
- **功能**:
  - 允许基岩版玩家加入Java版服务器
  - 自动协议转换
  - 支持所有主流功能

### 3. Floodgate
- **文件**: `plugins/floodgate-spigot.jar`
- **用途**: 基岩版玩家认证代理
- **功能**:
  - 允许基岩版玩家无需Java账号登录
  - 跨平台身份映射
  - 与GeyserMC配合使用

### 4. Fabric API
- **版本**: 0.98.0+1.20.6
- **文件**: `mods/fabric-api-0.98.0.jar`
- **用途**: Fabric模组基础API

## 快速启动

### 启动 PaperMC 服务端
```bash
cd paper
java -Xmx2G -jar paper.jar nogui
```

首次启动会生成:
- `eula.txt` - 需要同意EULA
- `server.properties` - 服务器配置
- `plugins/` - 插件目录

### 配置 GeyserMC
首次启动后，编辑 `plugins/Geyser-Spigot/config.yml`:
```yaml
bedrock:
  address: 0.0.0.0
  port: 19132
remote:
  address: auto
  port: 25565
```

### 配置 Floodgate
编辑 `plugins/floodgate/config.yml`:
```yaml
key-file-name: key.pem
username-prefix: "*"
```

## 协议分析用途

此服务端用于:
1. **Java版协议分析**: 研究 Minecraft Java 1.20.6 网络协议
2. **互通协议研究**: 分析 GeyserMC 如何将 Java 协议转换为基岩版协议
3. **数据包捕获**: 使用 Wireshark 捕获客户端-服务端通信
4. **逆向工程参考**: 对比迷你世界协议与 Minecraft 协议差异

## 网络端口

| 端口 | 用途 | 协议 |
|------|------|------|
| 25565 | Java版游戏端口 | TCP |
| 19132 | 基岩版游戏端口 | UDP |
| 19133 | 基岩版IPv6端口 | UDP |

## 下一步

1. 启动服务端并同意EULA
2. 配置GeyserMC和Floodgate
3. 使用Java版和基岩版客户端连接测试
4. 使用Wireshark捕获数据包进行分析
5. 对比迷你世界协议差异

---
Made with ❤️ by ZCNotFound for cross-platform gaming
