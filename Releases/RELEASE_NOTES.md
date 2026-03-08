# MnMCP v1.0.0_26w13a Release

**发布日期**: 2026-03-08

---

## 下载列表

| 文件 | 大小 | 说明 |
|------|------|------|
| `MnMCP-Core-v1.0.0_26w13a-Python.zip` | 0.5 MB | Python 核心协议引擎 (跨平台) — `pip install -e .` |
| `MnMCP-Personal-Windows-v1.0.0_26w13a.zip` | 11.6 MB | 玩家客户端 (Windows x64) — 连接到房主或服务器 |
| `MnMCP-Server-Windows-v1.0.0_26w13a.zip` | 11.2 MB | 服务器管理面板 (Windows x64) — 部署公共中继服务器 |
| `MnMCP-Streamer-Windows-v1.0.0_26w13a.zip` | 11.7 MB | 房主客户端 (Windows x64) — 创建房间让别人加入 |
| `MnMCP-v1.0.0_26w13a-Source-DevKit.zip` | 2.5 MB | 完整源代码 + 二次开发资源 |

## 使用说明

### Windows 客户端
1. 下载对应的 Windows zip 包
2. 解压到任意目录
3. 运行 `mnmcp_*.exe`

### Python 核心引擎
```bash
unzip MnMCP-Core-v1.0.0_26w13a-Python.zip
cd MnMCP-Core-v1.0.0_26w13a
pip install -e ".[dev]"
pytest  # 验证安装
```

### 二次开发
```bash
unzip MnMCP-v1.0.0_26w13a-Source-DevKit.zip
cd MnMCP-v1.0.0_26w13a

# Python 核心
cd mnmcp-core && pip install -e ".[dev]"

# Flutter 客户端 (需要 Flutter SDK >= 3.0)
cd mnmcp-personal && flutter pub get && flutter run -d windows
cd mnmcp-streamer && flutter pub get && flutter run -d windows
cd mnmcp-server && flutter pub get && flutter run -d windows
```

## 新特性

- 全新 MnMCP 2.0 架构，模块化设计
- 统一协议引擎: MC Bedrock ↔ MNW Protobuf 双向翻译
- 2969 条方块映射 + 实体/物品映射
- AES 加密: CBC (国服) + GCM (外服)
- 共享 Flutter 组件库 (三端统一 UI)
- 标准 Python 包 (`pyproject.toml` + pytest)
- 17/17 核心测试通过

## 系统要求

- **Windows 客户端**: Windows 10/11 x64, 4GB+ RAM
- **Python 核心**: Python 3.11+
- **二次开发**: Flutter SDK >= 3.0, Python 3.11+

## 已知限制

- Android 构建暂未包含 (需要 Android SDK)
- MNW Protobuf 协议解析尚不完整
- 端到端联机测试尚未完成

## 许可证

MIT License
