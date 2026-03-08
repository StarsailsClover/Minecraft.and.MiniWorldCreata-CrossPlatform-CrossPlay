# MnMCP Server

**版本**: 0.4.0  
**平台**: Windows / macOS / Linux  
**技术栈**: Flutter + Dart

---

## 📋 项目概述

MnMCP Server 是 MnMCP 跨平台联机系统的**公共服务器端**应用程序。

它提供：
- 多房间管理
- 玩家连接管理
- 协议桥接 (MNW ↔ MC)
- WebSocket + HTTP API
- 实时统计和日志

---

## 🚀 快速开始

### 前置要求

- Flutter SDK 3.0+
- Dart SDK 3.0+

### 安装依赖

```bash
flutter pub get
```

### 运行

```bash
run.bat
```

或手动：
```bash
flutter run -d windows
```

### 构建

```bash
# Windows
flutter build windows

# macOS
flutter build macos

# Linux
flutter build linux
```

---

## 🏗️ 架构

```
lib/
├── main.dart              # 入口
├── models/
│   ├── player.dart        # 玩家模型
│   └── room.dart          # 房间模型
├── services/
│   ├── server_service.dart    # 服务器核心
│   └── room_manager.dart      # 房间管理
├── screens/
│   └── home_screen.dart       # 主界面
└── widgets/
    ├── title_bar.dart         # 标题栏
    ├── server_status_card.dart # 状态卡片
    ├── room_list.dart         # 房间列表
    ├── player_list.dart       # 玩家列表
    └── log_viewer.dart        # 日志查看器
```

---

## 📡 API

### WebSocket

连接: `ws://localhost:8080/ws`

消息类型:
- `auth` - 认证
- `join_room` - 加入房间
- `leave_room` - 离开房间
- `create_room` - 创建房间
- `game_data` - 游戏数据

### HTTP API

- `GET /api/status` - 服务器状态
- `GET /api/rooms` - 房间列表

---

## 📝 配置

在 `ServerService` 中修改：

```dart
_tcpPort = 25565;      // TCP端口
_wsPort = 8080;        // WebSocket端口
_maxRooms = 100;       // 最大房间数
_maxPlayersPerRoom = 40;  // 每房间最大玩家
```

---

## 🎯 功能

- [x] 多房间管理
- [x] 玩家连接管理
- [x] WebSocket通信
- [x] HTTP API
- [x] 实时日志
- [ ] 协议桥接 (复用Personal端代码)
- [ ] 数据库持久化
- [ ] 负载均衡

---

## 📦 依赖

- `shelf` - HTTP服务器
- `web_socket_channel` - WebSocket
- `provider` - 状态管理
- `window_manager` - 窗口管理

---

## 🤝 与其他端的关系

```
[Personal端] ←→ [Server端] ←→ [Streamer端]
      ↓                              ↓
[MNW/MC客户端]                 [游戏世界]
```

---

## 📄 许可证

MIT License
