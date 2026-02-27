# 更新日志 (Changelog)

所有项目的显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 新增方块ID提取操作包 `MiniWorld_BlockID_Extraction_Package/`
  - Frida Hook脚本 `block_id_hook.js`
  - WebSocket抓包分析工具 `capture_websocket.py`
  - 完整操作指南和提交模板
- 新增协议分析报告 `docs/PROTOCOL_ANALYSIS_REPORT.md`
- 新增方块映射表 `src/protocol/block_mapping_complete.json`
- 新增坐标转换器 `src/protocol/coordinate_converter.py`
- 新增迷你世界认证模块 `src/protocol/miniworld_auth.py`

### Changed
- 更新 CI/CD 工作流至最新版本
  - `actions/checkout@v3` → `v4`
  - `actions/setup-python@v4` → `v5`
- 更新 README.md，添加项目状态徽章和架构图
- 优化 DEX 处理脚本路径配置

### Fixed
- 修复 `process_frida_dex.py` 路径指向错误
- 修复 CI 工作流中的依赖安装问题

## [1.0.0] - 2026-02-26

### Added
- 初始项目架构设计
- 协议翻译器核心框架
- 代理服务器基础实现
- 会话管理器
- 抓包工具链
- DEX 脱壳和分析工具
- 项目文档体系建立
  - TechnicalDocument.md
  - ProjectPlan.md
  - NextSteps.md
  - PROJECT_OVERVIEW.md
  - BeforeDevelopment.md

### 技术成果
- 识别 10+ 个迷你世界游戏服务器
- 分析 67,197 个数据包
- 完成 DEX 脱壳（81 个 DEX 文件）
- 建立基础协议映射表
- 完成 CI/CD 配置

---

## 版本说明

- **Unreleased**: 正在开发中的功能
- **1.0.0**: 项目初始版本，完成架构设计和基础分析

## 标签说明

- `Added`: 新添加的功能
- `Changed`: 对现有功能的变更
- `Deprecated`: 即将被移除的功能
- `Removed`: 已移除的功能
- `Fixed`: 修复的Bug
- `Security`: 安全相关的修复