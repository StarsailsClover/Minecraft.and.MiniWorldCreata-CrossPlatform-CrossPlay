# MnMCP v26.90.0 发布说明

**版本**: 26w14a_main_26.90.0  
**日期**: 2026-04-05  
**状态**: 正式版发布

---

## 概述

MnMCP (Minecraft and MiniWorld Cross-Platform CrossPlay) 是一个实现 Minecraft Java 版与迷你世界国服联机互通的项目。

---

## 功能特性

### ✅ 核心功能
- **协议转换**: Minecraft Java ↔ 迷你世界
- **加密通信**: ECDH + HKDF + AES-GCM
- **坐标转换**: 自动坐标系统转换
- **方块映射**: 36 种方块双向映射
- **实体映射**: 19 种实体双向映射

### ✅ 网络功能
- **UDP 连接**: 完整的 UDP 网络层
- **会话管理**: 自动密钥交换和会话维护
- **心跳机制**: 自动心跳保活
- **服务器配置**: 真实服务器地址 (从抓包获取)

### ✅ 业务功能
- **登录系统**: 完整的登录流程
- **房间管理**: 创建/加入/离开/搜索房间
- **聊天互通**: 双向聊天消息转发
- **玩家同步**: 位置和动作同步

### ✅ 工具链
- **抓包分析**: PCAPNG 文件解析
- **性能测试**: 全面的性能基准
- **集成测试**: 完整的模块测试

---

## 服务器配置

### 游戏服务器
```
116.205.254.229:19601  # 主要游戏服务器
116.205.254.229:19701  # 备用游戏服务器
```

### API 服务器
```
117.89.177.75:8080
118.89.46.203:8080
```

---

## 安装

```bash
# 克隆仓库
git clone https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git

# 安装依赖
pip install -r requirements.txt

# 可选: 安装真实加密库
pip install cryptography
```

---

## 快速开始

### 启动桥接器
```python
from src.bridge_v2 import MnMCPBridgeV2, BridgeV2Config

config = BridgeV2Config(
    mnw_username="your_username",
    mnw_password="your_password",
    mnw_world_id="world_id",
    enable_chat_bridge=True,
    enable_movement_bridge=True
)

bridge = MnMCPBridgeV2(config)
bridge.start()
```

### 运行测试
```bash
# 集成测试
python test_integration.py

# 性能测试
python test_performance.py

# 登录和房间测试
python test_login_room.py
```

---

## 项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── src/
│   ├── protocol/      # 协议层
│   ├── crypto/        # 加密层
│   ├── network/       # 网络层
│   ├── mapping/       # 映射层
│   ├── client/        # 客户端
│   ├── auth/          # 认证
│   ├── room/          # 房间管理
│   ├── config/        # 配置
│   ├── utils/         # 工具
│   ├── bridge.py      # 桥接器 V1
│   └── bridge_v2.py   # 桥接器 V2
├── tools/             # 工具脚本
├── tests/             # 测试
└── requirements.txt
```

---

## 性能指标

| 功能 | 性能 |
|------|------|
| HKDF 密钥派生 | 18,162 ops/s |
| AES-GCM 加密 | 14,165 ops/s |
| 坐标转换 | 1,145,299 ops/s |
| 方块映射 | 7,701,623 ops/s |
| 消息编码 | 1,295,698 ops/s |

---

## 版本历史

| 版本 | 说明 |
|------|------|
| 26w14a_main_26.90.0 | 正式版发布 |
| 26w14a_dev_26.1.9 | Phase 8-C: 优化完成 |
| 26w14a_dev_26.1.8 | Phase 8-A: 登录和房间 |
| 26w14a_dev_26.1.7 | Phase 7: 桥接器 V2 |
| 26w14a_main_26.89.0 | Phase 1-6 完成 |

---

## 许可证

MIT License

---

## 联系方式

- 项目主页: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
- 问题反馈: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/issues

---

## 致谢

感谢所有参与逆向工程和开发的人员！
