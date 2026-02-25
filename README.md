# Minecraft ↔ MiniWorld: Creata 全端互通联机方案

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Minecraft](https://img.shields.io/badge/Minecraft-Java%2F1.20.6%20%7C%20Bedrock-green)](https://www.minecraft.net/)
[![MiniWorld](https://img.shields.io/badge/MiniWorld-1.53.1%20%7C%201.7.15-orange)](https://www.mini1.cn/)

> 实现迷你世界（国服/外服·手游/PC）与 Minecraft（Java/Bedrock）全端互通联机的技术方案

---

## 项目简介

本项目旨在解决迷你世界与 Minecraft 两大沙盒游戏之间的跨平台联机互通问题，实现：

- **迷你世界四端兼容**：国服手游/PC、外服手游/PC
- **Minecraft 双版本互通**：Java版 + 基岩版
- **稳定联机体验**：方块/实体/聊天/挖掘/合成/背包无BUG
- **低延迟同步**：多人联机无卡顿、无位置漂移、无方块错乱

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      客户端层                                     │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│ 迷你国服手游  │ 迷你国服PC   │ 迷你外服手游  │ 迷你外服PC           │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                 │
       └─────────────┴──────┬──────┴─────────────────┘
                            ▼
              ┌─────────────────────────┐
              │      端适配层            │
              │  • 客户端类型识别        │
              │  • 加解密适配           │
              │  • 数据包裁剪/补全       │
              └───────────┬─────────────┘
                          ▼
              ┌─────────────────────────┐
              │     协议翻译层           │
              │  • 坐标修正(X轴取反)     │
              │  • ID映射转换           │
              │  • 操作指令翻译         │
              └───────────┬─────────────┘
                          ▼
              ┌─────────────────────────┐
              │   Java中转服务端         │
              │  PaperMC + Fabric       │
              └───────────┬─────────────┘
                          ▼
              ┌─────────────────────────┐
              │   GeyserMC + Floodgate  │
              │   Java ↔ Bedrock 桥接   │
              └───────────┬─────────────┘
                          ▼
       ┌──────────────────┴──────────────────┐
       ▼                                      ▼
┌─────────────┐                      ┌─────────────┐
│ MC Java版   │                      │ MC 基岩版   │
└─────────────┘                      └─────────────┘
```

---

## 支持版本

| 平台 | 版本 | 状态 |
|------|------|------|
| 迷你世界国服手游 | 1.53.1 | 计划中 |
| 迷你世界国服PC | 1.53.1 | 计划中 |
| 迷你世界外服手游 | MiniWorld: Creata 1.7.15 | 计划中 |
| 迷你世界外服PC | MiniWorld: Creata 1.7.15 | 计划中 |
| Minecraft Java | 1.20.6 | 计划中 |
| Minecraft Bedrock | 最新版 | 通过 GeyserMC 支持 |

---

## 快速开始

### 环境要求

- Python 3.8+
- Java 17+
- PaperMC 1.20.6
- Fabric Loader
- GeyserMC + Floodgate

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境（详见文档）
cp config.example.json config.json

# 4. 启动代理服务
python proxy_server.py
```

---

## 文档目录

| 文档 | 说明 |
|------|------|
| [docs/TechnicalDocument.md](./docs/TechnicalDocument.md) | 技术架构与实现文档 |
| [docs/ProjectPlan.md](./docs/ProjectPlan.md) | 项目规划与开发计划 |
| [ToDo.md](./ToDo.md) | 开发任务清单 |

---

## 核心特性

### 端适配层
- 自动识别客户端类型（国服/外服/手游/PC）
- 双加密算法支持（AES-128-CBC / AES-256-GCM）
- 动态房间人数限制（手游6人/PC40人）

### 协议翻译层
- 坐标系自动修正（解决方块镜像问题）
- 全量ID映射库（方块/实体/物品/粒子）
- 实时操作翻译（移动/挖掘/放置/聊天/合成）

### 网络优化
- 延迟补偿 + 帧插值算法
- 关键操作包重发机制
- 弱网环境自适应

---

## 开发路线图

- [ ] Java/Bedrock版Minecraft服务器联机协议整合与分析
- [ ] 迷你世界国服/外服协议逆向工程
- [ ] 端适配层开发
- [ ] 协议翻译层开发
- [ ] Java中转服务端集成
- [ ] GeyserMC对接与测试
- [ ] 多端联机功能测试
- [ ] 性能优化与文档完善

---

## 技术栈

- **后端**: Python, Java
- **游戏服务端**: PaperMC, Fabric
- **协议桥接**: GeyserMC, Floodgate
- **网络**: TCP/UDP, WebSocket
- **工具**: Wireshark, Frida, APKTool

---

## 免责声明

⚠️ **本项目仅供技术研究与学习使用**

- 禁止用于商业运营
- 不破解游戏本体、不盗用资源、不传播私服
- 使用本项目产生的任何后果由使用者自行承担

---

## 许可证

[MIT License](./LICENSE)

---

## 致谢

- [GeyserMC](https://github.com/GeyserMC/Geyser) - Java ↔ Bedrock 桥接方案
- [PaperMC](https://papermc.io/) - 高性能 Minecraft 服务端
- [Fabric](https://fabricmc.net/) - Minecraft 模组框架

---

<p align="center">
  Made with ❤️ by ZCNotFound for cross-platform gaming
</p>
