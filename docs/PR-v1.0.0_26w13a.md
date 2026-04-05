# PR: MnMCP v1.0.0_26w13a Phase 1 & Phase 2

**类型**: 版本发布 + 重大重构  
**版本**: v1.0.0_26w13a (Phase 1 + Phase 2)  
**状态**: Ready for Review

---

## 变更摘要

### Phase 1: 架构重构 (已完成 ✅)
- 全新模块化架构: `mnmcp-core/` + `mnmcp-shared/` + 三端客户端
- 消除所有 `sys.path` hack，转为标准 Python 包 (`pyproject.toml`)
- 合并重复实现 (3套代理/桥接/会话 → 1套统一实现)
- 修复致命 bug: MCPacketID 枚举冲突、codec 缺失、导入错误
- Windows 三端 exe 构建成功

### Phase 2: 协议逆向分析 (已完成 ✅)
- 深度分析 PC 端 DLL (`libSandBoxEngine.dll` 等 8 个关键文件)
- 提取 23,813 条网络相关字符串
- 分析 HTTP API 抓包数据 (mini1.cn 74 个端点)
- 校准 MNW 协议层:
  - 包头格式: 8 字节 LE (length + msg_type) ✅
  - 消息类型: 补充完整枚举 (1001-5009) ✅
  - Protobuf 编解码: 实现 varint/float/length-delimited ✅
- 生成协议校准报告 (`docs/20-Phase2-协议逆向分析报告.md`)

---

## 文件变更

### 新增
```
mnmcp-core/              # Python 核心协议引擎 (全新)
mnmcp-shared/            # Flutter 共享组件库 (全新)
mnmcp-personal/          # 玩家客户端 (重构)
mnmcp-streamer/          # 房主客户端 (重构)
mnmcp-server/            # 服务器面板 (重构)
mnmcp-website/           # 官网 (合并)
Releases/                # 5 个发布包 + RELEASE_NOTES.md
docs/20-Phase2-协议逆向分析报告.md
docs/PR-v1.0.0_26w13a.md (本文件)
```

### 修改
```
README.md                # 添加版本说明和快速开始
.gitignore               # 添加 *.pdb 和 **/windows/flutter/ephemeral/
mnmcp-core/src/mnmcp/protocol/__init__.py  # MNW 协议层校准
```

### 废弃 (已清理)
```
test_deploy/             # 已删除，引导使用 mnmcp-core/
旧项目中的冗余脚本和文档 → MnMCPResources/archived_v1/
```

---

## 测试

- [x] `mnmcp-core`: 17/17 pytest 通过
- [x] `mnmcp-server`: Windows exe 构建成功
- [x] `mnmcp-personal`: Windows exe 构建成功
- [x] `mnmcp-streamer`: Windows exe 构建成功
- [x] GitHub 上传检查: 0 FAIL, 35 PASS, 2 WARN (可接受)

---

## 已知限制

| 限制 | 说明 | 计划 |
|------|------|------|
| Android 支持 | 本版本暂未构建 | Phase 3 |
| iOS/macOS | 无支持计划 | N/A |
| MNW 协议验证 | 基于逆向推测，需实际联机验证 | Phase 3 |

---

## 审查清单

- [x] 代码风格符合项目规范 (Black + Ruff)
- [x] 所有测试通过
- [x] 敏感信息已脱敏
- [x] 大文件已排除 (`.gitignore`)
- [x] 文档已更新

---

## 合并后操作

1. 创建 GitHub Release
2. 上传 Releases/ 下的 5 个 zip 包
3. 关闭相关 Issue
