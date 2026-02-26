# MiniWorld 方块ID提取操作指南

## 📦 交付文件清单

本次交付包含以下文件，用于提取迷你世界（MiniWorld）国服 1.53.1 版本的方块ID：

### 1. 映射表文件（可直接使用）
- `block_mapping_complete.json` - 包含29个基础方块的推测映射（需验证）

### 2. 运行时提取工具（需要Root设备）
- `block_id_hook.js` - Frida脚本，用于Hook游戏进程获取方块ID
- `get_block_ids_runtime.py` - Python脚本生成器

### 3. 网络抓包分析工具
- `capture_websocket.py` - WebSocket数据包捕获分析

### 4. 完整操作指南
- 本文件（BLOCK_ID_EXTRACTION_GUIDE.md）

---

## 🎯 目标

从迷你世界国服PC端（或安卓端）提取方块ID映射表，建立以下对应关系：

| Minecraft方块ID | Minecraft名称 | 迷你世界方块ID | 迷你世界名称 |
|----------------|--------------|---------------|-------------|
| 1 | stone | ? | 石头 |
| 2 | grass_block | ? | 草方块 |
| ... | ... | ... | ... |

---

## 🔧 方法一：Frida运行时Hook（推荐）

### 前置要求
- **Root过的安卓设备** 或 **越狱的iOS设备**
- 已安装迷你世界国服（版本1.53.1）
- PC端安装：
  - Python 3.x
  - Frida: `pip install frida-tools`
  - ADB (Android Debug Bridge)

### 操作步骤

#### 步骤1：环境准备
```bash
# 1. 连接安卓设备到电脑，开启USB调试
adb devices

# 2. 确认设备已连接
# 应该显示设备序列号

# 3. 安装Frida-server到设备（需要Root）
# 下载对应架构的frida-server: https://github.com/frida/frida/releases
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

#### 步骤2：运行Frida脚本
```bash
# 使用生成的block_id_hook.js
frida -U -f com.minitech.miniworld -l block_id_hook.js --no-pause
```

#### 步骤3：在游戏中操作
1. 等待游戏完全加载进入主界面
2. 进入一个创造模式房间
3. 依次放置以下方块：
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
   - 其他需要映射的方块

4. 观察Frida输出，记录每个方块对应的ID值

#### 步骤4：记录结果
将观察到的方块ID填入以下表格：

```
石头: __
草方块: __
泥土: __
圆石: __
木板: __
沙子: __
玻璃: __
金矿石: __
铁矿石: __
钻石矿石: __
...（其他方块）
```

---

## 📡 方法二：网络抓包分析

### 前置要求
- PC已安装迷你世界国服
- Wireshark 或 mitmproxy
- 能够拦截WebSocket流量（可能需要代理设置）

### 操作步骤

#### 步骤1：设置抓包环境
```bash
# 使用mitmproxy拦截HTTPS/WebSocket
mitmproxy --mode transparent --showhost

# 或者在路由器层面抓包
```

#### 步骤2：捕获游戏流量
1. 启动抓包工具
2. 启动迷你世界并登录
3. 进入一个游戏房间
4. 开始捕获数据包

#### 步骤3：分析数据包
运行提供的Python分析脚本：
```bash
python capture_websocket.py --pcap captured_traffic.pcapng
```

#### 步骤4：定位方块数据
在捕获的流量中查找：
- WebSocket连接到 `wskacchm.mini1.cn:4000`
- 数据包中包含方块放置操作
- 分析数据包结构，找到方块ID字段

---

## 🔍 方法三：内存搜索（高级）

### 使用Cheat Engine / GameGuardian

#### 步骤1：定位内存区域
1. 启动迷你世界
2. 进入游戏世界
3. 使用内存搜索工具
4. 搜索已知数值（如背包中某种方块的数量）

#### 步骤2：追踪方块ID
1. 放置一个方块
2. 搜索变化的数值
3. 重复直到找到方块ID存储位置
4. 导出内存区域进行分析

---

## 📋 方法四：资源文件分析

### 检查APK文件

#### 步骤1：解压APK
```bash
# APK文件通常位于:
# Android: /data/app/com.minitech.miniworld-*/base.apk

# 解压APK
unzip miniworld.apk -d miniworld_extracted/
```

#### 步骤2：查找资源文件
```bash
# 搜索可能的方块定义文件
cd miniworld_extracted

# 查找JSON配置文件
find . -name "*.json" | xargs grep -l "block\|Block\|方块" 2>/dev/null

# 查找二进制数据文件
find . -name "*.dat" -o -name "*.bin" | head -20

# 查找Unity资源文件
find . -name "*.assets" -o -name "*.resource"
```

#### 步骤3：分析Unity资源
如果游戏使用Unity引擎：
```bash
# 使用AssetStudio或类似工具提取Unity资源
# 查找包含方块定义的ScriptableObject
```

---

## 📝 结果提交格式

提取到方块ID后，请按以下格式提交：

### 1. 方块ID列表（JSON格式）
```json
{
  "version": "1.53.1",
  "extraction_method": "frida_hook",
  "blocks": [
    {"mnw_id": 1, "mnw_name": "石头", "mc_id": 1, "mc_name": "minecraft:stone"},
    {"mnw_id": 2, "mnw_name": "草方块", "mc_id": 2, "mc_name": "minecraft:grass_block"},
    {"mnw_id": 3, "mnw_name": "泥土", "mc_id": 3, "mc_name": "minecraft:dirt"}
    // ... 更多方块
  ]
}
```

### 2. 提取日志
- 使用的提取方法
- 设备信息（型号、系统版本）
- 遇到的问题和解决方案

### 3. 验证截图
- 游戏内放置方块的截图
- 对应的ID值截图（Frida输出或内存查看器）

---

## ⚠️ 注意事项

1. **法律合规**：仅在个人设备上进行逆向工程，不要分发修改后的游戏文件
2. **账号安全**：使用小号进行测试，避免主账号被封禁
3. **数据备份**：操作前备份重要数据
4. **Root风险**：Root设备可能失去保修，谨慎操作

---

## 📞 技术支持

如遇到问题，请提供以下信息：
1. 设备型号和系统版本
2. 使用的提取方法
3. 具体的错误信息或截图
4. 已经尝试的解决步骤

---

## 📦 附录：交付文件详细说明

### block_mapping_complete.json
- **用途**：开发参考，包含29个基础方块的推测映射
- **状态**：`verified: false` 表示需要验证
- **格式**：JSON，可直接被Python/Java读取

### block_id_hook.js
- **用途**：Frida脚本，Hook游戏进程
- **使用方法**：`frida -U -f com.minitech.miniworld -l block_id_hook.js`
- **预期输出**：函数调用日志，包含方块ID参数

### get_block_ids_runtime.py
- **用途**：生成Frida脚本和打印操作指南
- **运行**：`python get_block_ids_runtime.py`

### capture_websocket.py
- **用途**：分析WebSocket抓包数据
- **使用方法**：`python capture_websocket.py --pcap capture.pcapng`

---

**文档版本**: 1.0  
**更新日期**: 2026-02-26  
**适用游戏版本**: MiniWorld 国服 1.53.1