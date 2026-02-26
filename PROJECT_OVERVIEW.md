# Minecraft ↔ MiniWorld 全端互通联机方案

## 项目总览

> 实现迷你世界（国服/外服·手游/PC）与 Minecraft（Java/Bedrock）全端互通联机的技术方案

---

## 项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/  [GitHub仓库]
├── 📁 apk_downloads/              # APK下载和反编译脚本
│   ├── decompile_checkpoint.py    # 断点续传式反编译 ⭐
│   ├── download_apk.py           # APK下载脚本
│   ├── MANUAL_DOWNLOAD_GUIDE.md  # 手动下载指南
│   └── DECOMPILE_GUIDE.md        # 反编译指南
│
├── 📁 docs/                       # 技术文档
│   ├── TechnicalDocument.md      # 技术架构文档
│   ├── ProjectPlan.md            # 项目规划文档
│   └── README.md                 # 文档说明
│
├── 📁 protocol_analysis/          # 协议分析模块 ⭐
│   ├── packet_analyzer.py        # 数据包分析器
│   └── README.md                 # 模块文档
│
├── 📁 reverse_engineering/        # 逆向工程记录
│   └── session_*.md              # 会话记录
│
├── 📁 server/                     # Minecraft服务端
│   ├── paper/                    # PaperMC
│   ├── plugins/                  # GeyserMC + Floodgate
│   ├── fabric/                   # Fabric模组
│   └── mods/                     # Fabric API
│
├── 📁 tools/                      # 逆向工程工具
│   ├── apktool.jar              # APK反编译
│   ├── jadx/                    # Java反编译器
│   └── ...
│
├── 📄 path_resolver.py           # 统一路径解析工具 ⭐
├── 📄 check_and_fix_components.py # 组件完整性检查 ⭐
├── 📄 COMPONENT_MANIFEST.json    # 组件清单 ⭐
├── 📄 PROJECT_OVERVIEW.md        # 本文件 ⭐
└── 📄 README.md                  # 项目主文档

MnMCPResources/                   # 外部资源目录 [不在GitHub]
└── 📁 apk_downloads/
    └── miniworld_cn_1.53.1.apk  # 迷你世界国服 (1.60 GB)
```

---

## 核心功能模块

### 1. 断点续传式反编译 ⭐

**文件**: `apk_downloads/decompile_checkpoint.py`

**功能**:
- ✅ 支持断点续传（崩溃后可恢复）
- ✅ 实时进度保存
- ✅ 详细日志记录
- ✅ 自动错误重试
- ✅ 阶段状态追踪

**使用**:
```bash
# 启动反编译（后台运行）
python decompile_checkpoint.py

# 查看状态
python decompile_checkpoint.py status

# 重置检查点
python decompile_checkpoint.py reset
```

**检查点文件**: `reverse_engineering/decompile_checkpoint.json`

---

### 2. 统一路径解析系统 ⭐

**文件**: `path_resolver.py`

**功能**:
- ✅ 自动处理外部目录
- ✅ 支持.location文件
- ✅ 向后兼容项目目录
- ✅ 简化路径管理

**使用**:
```python
import path_resolver

# 获取APK路径
apk = path_resolver.get_apk_path("miniworld_cn_1.53.1.apk")

# 获取工具路径
tool = path_resolver.get_tool_path("apktool.jar")

# 获取服务端路径
server = path_resolver.get_server_path("paper/paper.jar")
```

---

### 3. 协议分析模块 ⭐

**目录**: `protocol_analysis/`

**功能**:
- ✅ Minecraft Java 1.20.6 协议解析
- ✅ VarInt/字符串解析
- ✅ 数据包结构定义
- ✅ 协议报告生成

**使用**:
```python
from protocol_analysis.packet_analyzer import MinecraftJavaProtocol

# 获取数据包信息
packet = MinecraftJavaProtocol.get_packet_info(0x0F)

# 生成协议报告
report = generate_protocol_report()
```

---

### 4. 组件完整性检查 ⭐

**文件**: `check_and_fix_components.py`

**功能**:
- ✅ 自动检查所有组件
- ✅ 修复路径问题
- ✅ 生成组件清单
- ✅ 验证外部引用

**使用**:
```bash
python check_and_fix_components.py
```

---

## 快速开始

### 新成员设置（5分钟）

```bash
# 1. 克隆仓库
git clone <repo-url>
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay

# 2. 创建外部目录
mkdir C:\Users\<用户名>\Documents\Coding\MnMCPResources

# 3. 下载APK（参考 MANUAL_DOWNLOAD_GUIDE.md）
# 保存到: MnMCPResources/apk_downloads/

# 4. 验证路径
python path_resolver.py

# 5. 检查完整性
python check_and_fix_components.py

# 6. 启动反编译
python apk_downloads/decompile_checkpoint.py
```

### 日常使用

```bash
# 查看反编译状态
python apk_downloads/decompile_checkpoint.py status

# 生成协议报告
python protocol_analysis/packet_analyzer.py

# 启动Minecraft服务端
server/start.bat
```

---

## 当前进度

### 已完成 ✅

| 模块 | 状态 | 说明 |
|------|------|------|
| 项目架构 | ✅ | 完整目录结构 |
| 服务端搭建 | ✅ | PaperMC + GeyserMC |
| 工具准备 | ✅ | apktool, jadx, frida |
| 路径系统 | ✅ | 统一路径解析 |
| 组件检查 | ✅ | 完整性验证 |
| 协议分析模块 | ✅ | Minecraft Java协议 |
| 断点反编译 | ✅ | 支持续传 |
| APK下载 | ✅ | 迷你世界国服 |

### 进行中 🔄

| 任务 | 状态 | 预计完成 |
|------|------|----------|
| APK反编译 | 🔄 | 20-30分钟 |
| 协议逆向 | ⏳ | 等待反编译 |

### 待开始 ⏳

| 任务 | 优先级 | 说明 |
|------|--------|------|
| 下载外服APK | 高 | MiniWorld: Creata |
| 下载MC基岩APK | 中 | 需正版购买 |
| Wireshark配置 | 中 | 抓包分析 |
| 协议映射表 | 高 | ID映射构建 |
| 代理服务器 | 高 | 核心功能 |

---

## 技术栈

### 逆向工程
- **APK反编译**: apktool 2.9.3
- **Java反编译**: jadx 1.4.7
- **动态分析**: frida 16.1.11
- **抓包工具**: Wireshark

### Minecraft服务端
- **核心**: PaperMC 1.20.6
- **互通**: GeyserMC 2.3.1
- **认证**: Floodgate
- **模组**: Fabric 0.98.0

### 开发语言
- **Python 3.11**: 协议分析、自动化脚本
- **Java**: 服务端、反编译
- **Smali**: Android字节码分析

---

## 文档索引

| 文档 | 用途 | 位置 |
|------|------|------|
| PROJECT_OVERVIEW.md | 项目总览 | 根目录 |
| README.md | 项目介绍 | 根目录 |
| TechnicalDocument.md | 技术架构 | docs/ |
| ProjectPlan.md | 开发计划 | docs/ |
| MANUAL_DOWNLOAD_GUIDE.md | APK下载指南 | apk_downloads/ |
| DECOMPILE_GUIDE.md | 反编译指南 | apk_downloads/ |
| COMPONENT_MANIFEST.json | 组件清单 | 根目录 |
| EXTERNAL_RESOURCES.md | 外部资源说明 | 根目录 |

---

## 贡献指南

### 代码规范
- 使用 `path_resolver.py` 获取路径
- 大文件(>100MB)放入外部目录
- 更新 `COMPONENT_MANIFEST.json`
- 记录会话到 `reverse_engineering/`

### 提交检查清单
- [ ] 运行 `check_and_fix_components.py`
- [ ] 检查大文件位置
- [ ] 更新文档
- [ ] 测试路径解析

---

## 许可证

MIT License - 仅供技术研究与学习使用

---

Made with ❤️ by ZCNotFound for cross-platform gaming

**最后更新**: 2026-02-26
