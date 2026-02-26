# 📦 MiniWorld 方块ID提取 - 操作员包

## 这是给谁的？

这个包是给**有Root安卓设备**的技术人员使用的，用于从迷你世界游戏中提取方块ID映射表。

## 📂 包内容

```
MiniWorld_BlockID_Extraction_Package/
├── 📄 BLOCK_ID_EXTRACTION_GUIDE.md    # 完整操作指南（详细步骤）
├── 📄 README_FOR_OPERATOR.md          # 本文件（快速开始）
├── 🔧 block_id_hook.js                # Frida脚本（运行时Hook）
├── 🔧 get_block_ids_runtime.py        # Python脚本生成器
├── 🔧 capture_websocket.py            # 抓包分析工具
├── 📊 block_mapping_complete.json     # 基础映射表（29个方块，待验证）
└── 📋 block_mapping_template.json     # 空白模板（需填写）
```

## 🚀 快速开始（3步法）

### 第1步：环境准备
```bash
# 在电脑上安装Frida
pip install frida-tools

# 确认安卓设备已Root并开启USB调试
adb devices
```

### 第2步：运行Frida脚本
```bash
# 将block_id_hook.js推送到设备
adb push block_id_hook.js /data/local/tmp/

# 运行Frida Hook
frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause
```

### 第3步：游戏中操作并记录
1. 等待游戏加载
2. 进入创造模式房间
3. 依次放置以下方块并记录ID：
   - 石头
   - 草方块
   - 泥土
   - 圆石
   - 木板
   - 沙子
   - 玻璃
   - 金矿石
   - 铁矿石
   - 钻石矿石
   - （其他需要的方块）

## 📝 需要提交的产出

### 必须提交：
1. **方块ID列表**（JSON格式）
2. **操作日志**（遇到的问题和解决方式）

### 可选提交：
3. **截图**（Frida输出、游戏画面）
4. **抓包文件**（如果使用抓包方法）

## 📊 提交格式示例

```json
{
  "version": "1.53.1",
  "extraction_method": "frida_hook",
  "device": "小米13 / Android 14",
  "blocks": [
    {"mnw_id": 1, "mnw_name": "石头", "mc_id": 1, "mc_name": "minecraft:stone"},
    {"mnw_id": 2, "mnw_name": "草方块", "mc_id": 2, "mc_name": "minecraft:grass_block"},
    {"mnw_id": 3, "mnw_name": "泥土", "mc_id": 3, "mc_name": "minecraft:dirt"}
  ]
}
```

## ⚠️ 重要提示

1. **使用小号测试** - 避免主账号风险
2. **仅在个人设备操作** - 不要用于非法用途
3. **遇到问题先看详细指南** - BLOCK_ID_EXTRACTION_GUIDE.md

## 📞 联系方式

如果遇到问题：
1. 记录错误信息
2. 截图相关画面
3. 联系项目开发者

---

**祝提取顺利！**