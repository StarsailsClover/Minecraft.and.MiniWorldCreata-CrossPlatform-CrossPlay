# Agent改动记录

**时间**: 2026-02-26  
**Agent**: 之前的对话Agent  
**操作**: 方块ID提取工具包创建

---

## 📦 新增文件清单

### 1. 文档文件

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| README_FOR_OPERATOR.md | tools/ | 2.7 KB | 操作员快速开始指南 |
| BLOCK_ID_EXTRACTION_GUIDE.md | docs/ | 2.6 KB | 完整方块ID提取指南 |
| manual_search_guide.md | tools/ | 未知 | 手动搜索指南 |

### 2. Python脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| capture_websocket.py | tools/ | WebSocket抓包分析工具 |
| get_block_ids_runtime.py | tools/ | 运行时方块ID获取 |

### 3. PowerShell脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| analyze_dex_structure.ps1 | tools/ | DEX结构分析 |
| extract_block_ids_v2.ps1 | tools/ | 方块ID提取v2 |
| extract_mnw_blocks.ps1 | tools/ | MNW方块提取 |

### 4. Batch脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| apktool.bat | tools/ | APK工具 |
| debug_dex.bat | tools/ | DEX调试 |
| extract_from_subdirs.bat | tools/ | 子目录提取 |
| extract_simple.bat | tools/ | 简单提取 |
| quick_extract.bat | tools/ | 快速提取 |
| setup_env.bat | tools/ | 环境设置 |

### 5. 数据文件

| 文件 | 路径 | 说明 |
|------|------|------|
| extracted_blocks.json | tools/ | 提取的方块数据（空） |
| block_mapping_complete.json | src/protocol/ | 完整方块映射 |

---

## 🎯 改动目的

Agent创建了一套完整的**方块ID提取工具包**，用于：

1. **从迷你世界游戏中提取方块ID映射表**
2. **建立Minecraft和迷你世界方块ID的对应关系**
3. **支持多种提取方法**：
   - Frida运行时Hook（推荐）
   - WebSocket抓包分析
   - DEX静态分析

---

## 📋 工具包内容

### 交付物清单

```
MiniWorld_BlockID_Extraction_Package/
├── 📄 BLOCK_ID_EXTRACTION_GUIDE.md    # 完整操作指南
├── 📄 README_FOR_OPERATOR.md          # 快速开始
├── 🔧 block_id_hook.js                # Frida脚本
├── 🔧 get_block_ids_runtime.py        # Python生成器
├── 🔧 capture_websocket.py            # 抓包工具
├── 📊 block_mapping_complete.json     # 基础映射表
└── 📋 block_mapping_template.json     # 空白模板
```

---

## 🔧 使用方法

### 方法1: Frida运行时Hook（推荐）

```bash
# 1. 环境准备
pip install frida-tools
adb devices

# 2. 运行Frida脚本
frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause

# 3. 游戏中操作并记录
```

### 方法2: WebSocket抓包

```bash
python tools/capture_websocket.py --pcap capture.pcapng
```

### 方法3: DEX静态分析

```powershell
# Windows
.\tools\analyze_dex_structure.ps1
```

---

## ⚠️ 重要提示

1. **需要Root设备** - 大部分工具需要Root过的安卓设备
2. **使用小号测试** - 避免主账号风险
3. **仅在个人设备操作** - 不要用于非法用途

---

## 📊 当前方块映射状态

### 已有映射（29个基础方块）
- 石头、草方块、泥土、圆石等
- 状态：推测映射，待验证

### 待提取方块
- 所有其他方块ID
- 需要通过上述工具提取

---

## 🔗 相关文件

- 详细指南: `docs/BLOCK_ID_EXTRACTION_GUIDE.md`
- 快速开始: `tools/README_FOR_OPERATOR.md`
- 基础映射: `src/protocol/block_mapping_complete.json`

---

## 📝 后续任务

1. [ ] 使用Frida提取实际方块ID
2. [ ] 验证现有29个方块映射
3. [ ] 补充完整方块映射表
4. [ ] 测试方块转换功能

---

**记录时间**: 2026-02-26  
**记录人**: 当前Agent
