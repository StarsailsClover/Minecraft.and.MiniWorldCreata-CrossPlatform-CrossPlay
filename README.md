# MnMCP - Minecraft and MiniWorld Cross-Platform CrossPlay

**版本**: 26w14a_main_26.89.0  
**状态**: Phase 1-6 已完成，正式版发布

---

## 项目简介

MnMCP 是一个跨平台的 Minecraft 与迷你世界互通项目，允许 Minecraft Java 版玩家和迷你世界国服玩家在同一个世界中游戏。

### 核心功能
- ✅ Minecraft Java 协议支持
- ✅ 迷你世界国服协议支持 (iLink/mmtls)
- ✅ ECDH + AES-GCM 加密通信
- ✅ 方块/实体/物品映射
- ✅ 玩家状态同步
- ✅ 聊天消息互通

---

## 架构

```
src/
├── protocol/      # 协议层
│   ├── mc_java.py    # Minecraft Java 协议
│   ├── ilink.py      # iLink/mmtls 协议
│   ├── raknet.py     # RakNet 适配
│   ├── mnw.py        # 迷你世界协议
│   └── business.py   # 业务协议
├── crypto/        # 加密层 (ECDH + HKDF + AES-GCM)
├── network/       # 网络层 (UDP + Session)
├── mapping/       # 映射层 (方块/实体/物品/坐标)
└── bridge.py      # 核心桥接器
```

---

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行桥接器
```bash
python -m src.bridge
```

### 运行测试
```bash
python test_crypto_manual.py
python test_network_manual.py
python test_bridge_manual.py
python test_mc_java_manual.py
```

---

## 开发进度

- [x] Phase 1: 基础框架
- [x] Phase 2: 加密层
- [x] Phase 3: 网络层
- [x] Phase 4: 业务协议层
- [x] Phase 5: 映射层 + 桥接核心
- [x] Phase 6: Minecraft Java 协议
- [ ] Phase 7: 完整联机功能 (开发中)

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 26w14a_main_26.89.0 | 2026-04-05 | Phase 1-6 完成，正式版 |
| 26w14a_dev_26.1.6 | 2026-04-05 | Phase 6: MC Java 协议 |
| 26w14a_dev_26.1.5 | 2026-04-05 | Phase 5: 映射层 + 桥接器 |
| 26w14a_dev_26.1.4 | 2026-04-05 | Phase 4: 业务协议层 |
| 26w14a_dev_26.1.3 | 2026-04-05 | Phase 3: 网络层 |
| 26w14a_dev_26.1.2 | 2026-04-05 | Phase 2: 加密层 |
| 26w14a_dev_26.1.1 | 2026-04-05 | Phase 1: 基础框架 |

---

## 许可证

MIT License

---

## 联系方式

- 项目主页: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
