# MnMCP 简介

## 什么是 MnMCP？

**MnMCP** (Minecraft and MiniWorld Creata Cross-Platform) 是一个实现 **Minecraft** 与 **迷你世界** 跨平台联机的开源代理服务器。

它允许两个游戏的玩家在同一个虚拟世界中互动，打破了平台壁垒。

## 核心功能

### ✅ 双向协议翻译
- Minecraft 协议 ↔ 迷你世界协议
- 实时数据包转换
- 支持多种数据类型

### ✅ 方块同步
- 2228 个方块ID映射
- 方块放置/破坏同步
- 方块状态转换

### ✅ 玩家交互
- 位置同步
- 聊天消息转发
- 玩家动作同步

### ✅ 安全加密
- AES-128-CBC 加密（国服）
- AES-256-GCM 加密（外服）
- 密码双重MD5哈希

## 技术亮点

| 特性 | 说明 |
|------|------|
| **异步架构** | 基于 asyncio 的高性能网络处理 |
| **协议兼容** | 支持 Minecraft 1.20.6+ 和迷你世界 1.53.1+ |
| **性能优化** | 支持 100+ 并发连接 |
| **易于部署** | 一键安装脚本，自动依赖管理 |

## 适用场景

- 🎮 **朋友联机**：让玩不同游戏的朋友一起玩
- 🏠 **家庭娱乐**：家庭成员使用不同设备联机
- 🎓 **技术学习**：学习游戏协议和网络编程
- 🔧 **开发测试**：测试跨平台兼容性

## 快速开始

### 1. 安装

```bash
pip install websockets pyyaml
```

### 2. 启动

```bash
python start.py
```

### 3. 连接

- Minecraft 连接 `127.0.0.1:19132`
- 迷你世界连接 `127.0.0.1:8080`

## 项目状态

- **版本**: v0.6.0
- **状态**: 稳定运行
- **测试通过率**: 97.6%
- **方块映射**: 2228 个

## 开源协议

MIT License - 自由使用、修改和分发

## 社区

- **GitHub**: [starsailsclover/MnMCP](https://github.com/starsailsclover/MnMCP)
- **QQ群**: 1084172731
- **官网**: [MnMCP介绍站](https://starsailsclover.github.io/MnMCP-Introducing-Website/)

## 下一步

- [安装部署](installation.html)
- [使用指南](usage.html)
- [开发文档](../dev/architecture.html)
