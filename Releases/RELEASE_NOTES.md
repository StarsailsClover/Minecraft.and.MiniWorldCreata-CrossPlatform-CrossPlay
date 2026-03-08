# MnMCP v1.0.0_26w13a Release Notes

**发布日期**: 2026-03-08

---

## 下载

| 文件 | 说明 |
|------|------|
| `MnMCP-Personal-Windows.zip` | 玩家客户端 (Windows x64) |
| `MnMCP-Streamer-Windows.zip` | 房主客户端 (Windows x64) |
| `MnMCP-Server-Windows.zip` | 服务器管理面板 (Windows x64) |
| `MnMCP-Core-v1.0.0_26w13a-Python.zip` | Python 核心引擎 (跨平台) |
| `MnMCP-v1.0.0_26w13a-Source-DevKit.zip` | 完整源代码 + 二次开发资源 |

## 新特性

- **全新架构**: MnMCP 2.0 完全重写, 模块化设计
- **统一协议引擎**: MC Bedrock ↔ MNW Protobuf 双向翻译
- **2969 方块映射**: 完整的方块 ID 双向映射
- **AES 加密**: 支持 CBC (国服) 和 GCM (外服)
- **共享组件库**: 三端共用 Flutter 组件
- **Android 原生层**: Kotlin VPN Service + 前台服务
- **标准 Python 包**: `pip install -e .` 即可使用

## 系统要求

### Windows 客户端
- Windows 10/11 x64
- 4GB+ RAM

### Python 核心引擎
- Python 3.11+
- `pip install -e ".[dev]"` 安装依赖

### 二次开发
- Flutter SDK >= 3.0
- Python 3.11+
- Android Studio (Android 构建)

## 已知问题

- MNW Protobuf 协议解析尚不完整, 部分消息类型需要逆向确认
- 端到端联机测试尚未完成
- iOS 暂不支持
