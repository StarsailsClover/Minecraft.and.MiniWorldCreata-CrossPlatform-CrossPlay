# 方块ID提取工具包说明

**创建时间**: 2026-02-26  
**创建Agent**: 前一个对话Agent  
**用途**: 从迷你世界提取方块ID映射表

---

## 📦 工具包概述

Agent创建了一套完整的工具包，用于提取迷你世界（MiniWorld）国服 1.53.1 版本的方块ID，建立与Minecraft方块ID的映射关系。

---

## 📂 文件清单

### 核心文档
| 文件 | 路径 | 说明 |
|------|------|------|
| BLOCK_ID_EXTRACTION_GUIDE.md | docs/ | 完整操作指南 |
| README_FOR_OPERATOR.md | tools/ | 操作员快速开始 |
| manual_search_guide.md | tools/ | 手动搜索指南 |

### Python工具
| 文件 | 路径 | 说明 |
|------|------|------|
| capture_websocket.py | tools/ | WebSocket抓包分析 |
| get_block_ids_runtime.py | tools/ | 运行时ID获取 |

### PowerShell脚本
| 文件 | 路径 | 说明 |
|------|------|------|
| analyze_dex_structure.ps1 | tools/ | DEX结构分析 |
| extract_block_ids_v2.ps1 | tools/ | 方块ID提取v2 |
| extract_mnw_blocks.ps1 | tools/ | MNW方块提取 |

### Batch脚本
| 文件 | 路径 | 说明 |
|------|------|------|
| apktool.bat | tools/ | APK工具 |
| debug_dex.bat | tools/ | DEX调试 |
| extract_from_subdirs.bat | tools/ | 子目录提取 |
| extract_simple.bat | tools/ | 简单提取 |
| quick_extract.bat | tools/ | 快速提取 |
| setup_env.bat | tools/ | 环境设置 |

### 数据文件
| 文件 | 路径 | 说明 |
|------|------|------|
| block_mapping_complete.json | src/protocol/ | 29个方块映射表 |
| extracted_blocks.json | tools/ | 提取结果（空） |

---

## 🎯 三种提取方法

### 方法1: Frida运行时Hook（推荐）
**适用**: 有Root安卓设备

```bash
# 安装Frida
pip install frida-tools

# 连接设备
adb devices

# 运行Hook
frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause
```

**优点**:
- 最准确的方法
- 实时获取游戏内ID

**缺点**:
- 需要Root设备
- 需要一定技术基础

### 方法2: WebSocket抓包
**适用**: 有抓包环境

```bash
python tools/capture_websocket.py --pcap capture.pcapng
```

**优点**:
- 无需Root
- 可分析网络通信

**缺点**:
- 需要抓包环境
- 数据可能加密

### 方法3: DEX静态分析
**适用**: 有DEX文件

```powershell
# Windows
.\tools\analyze_dex_structure.ps1
```

**优点**:
- 无需运行游戏
- 可批量分析

**缺点**:
- 代码可能混淆
- 需要逆向经验

---

## 📊 当前方块映射状态

### 已有映射（29个基础方块）

```json
{
  "mc_id": 1,      // Minecraft方块ID
  "mc_name": "石头", // Minecraft名称
  "mnw_id": 1,     // 迷你世界方块ID（推测）
  "mnw_name": "stone",
  "verified": false  // 待验证
}
```

**方块列表**:
1. 空气 (air)
2. 石头 (stone)
3. 草方块 (grass)
4. 泥土 (dirt)
5. 圆石 (cobblestone)
6. 橡木木板 (wood_plank)
7. 基岩 (bedrock)
8. 沙子 (sand)
9. 砾石 (gravel)
10. 金矿石 (gold_ore)
11. 铁矿石 (iron_ore)
12. 煤矿石 (coal_ore)
...（共29个）

### 待提取方块
- 所有其他方块
- 需要通过上述工具提取

---

## 🚀 快速开始

### 有Root设备的用户

1. **阅读快速开始指南**
   ```
   tools/README_FOR_OPERATOR.md
   ```

2. **准备环境**
   ```bash
   pip install frida-tools
   adb devices
   ```

3. **运行提取**
   ```bash
   frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause
   ```

4. **游戏中操作**
   - 进入创造模式
   - 依次放置方块
   - 记录Frida输出

### 无Root设备的用户

1. **使用抓包方法**
   ```bash
   python tools/capture_websocket.py
   ```

2. **或使用静态分析**
   ```powershell
   .\tools\analyze_dex_structure.ps1
   ```

---

## ⚠️ 重要提示

1. **使用小号测试** - 避免主账号风险
2. **仅在个人设备操作** - 不要用于非法用途
3. **备份重要数据** - 防止意外丢失

---

## 📞 获取帮助

- 详细指南: `docs/BLOCK_ID_EXTRACTION_GUIDE.md`
- 快速开始: `tools/README_FOR_OPERATOR.md`
- 问题反馈: 提交Issue

---

## 📝 提交结果

提取完成后，请提交：

```json
{
  "version": "1.53.1",
  "extraction_method": "frida_hook",
  "device": "设备型号",
  "blocks": [
    {"mnw_id": 1, "mnw_name": "石头", "mc_id": 1, "mc_name": "minecraft:stone"}
  ]
}
```

---

**祝提取顺利！**
