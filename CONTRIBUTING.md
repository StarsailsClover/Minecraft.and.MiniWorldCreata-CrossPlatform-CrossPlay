# Contributing to MnMCP

感谢你对 MnMCP 项目的兴趣！

## 开发环境

### 核心引擎 (Python)

```bash
cd mnmcp-core
pip install -e ".[dev]"
pytest                    # 运行测试
black src/ tests/         # 格式化
ruff check src/ tests/    # 代码检查
```

### Flutter 客户端

```bash
flutter pub get
flutter analyze
flutter test
```

## 项目规范

### 分支策略

- `main` — 稳定发布分支
- `develop` — 开发分支
- `feature/*` — 功能分支
- `fix/*` — 修复分支

### 提交规范

```
<type>(<scope>): <description>

type: feat, fix, docs, style, refactor, test, chore
scope: core, personal, streamer, server, shared, website
```

示例:
```
feat(core): add MNW protobuf message parser
fix(personal): resolve VPN connection timeout
docs(readme): update quick start guide
```

### 代码风格

- Python: Black (line-length=100) + Ruff
- Dart: `flutter analyze` 无警告
- Kotlin: Android Studio 默认格式化

## 版本号

`v{major}.{minor}.{patch}_{year}w{week}{letter}`

示例: `v1.0.0_26w13a`

- 语义化版本 (major.minor.patch)
- Minecraft 快照风格 (年份w周数+字母)

## 需要帮助的领域

- MNW Protobuf 协议逆向分析
- 更多方块/实体/物品映射验证
- iOS Flutter 适配
- 性能优化和压力测试
