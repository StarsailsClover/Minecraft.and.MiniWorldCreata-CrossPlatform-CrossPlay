# 逆向工程会话记录 - Session 011
## 任务: 检查新文件结构 + 开始双端反编译和分析
## 开始时间: 2026-02-26 02:15
## 完成时间: 2026-02-26 02:30

### 用户操作更新
- ✅ 重命名: apk_downloads → packs_downloads
- ✅ 下载: com.minitech.miniworld.uc.apk（UC/九游渠道服，1.6GB）
- ✅ 下载: miniworld.exe（PC版安装程序）
- ✅ 安装: PC版到 miniworldPC_CN
- ⏳ 游戏资源文件更新中

---

### 步骤 1: 更新路径解析器

**修改**: `path_resolver.py`

**新功能**:
- 支持 packs_downloads（新目录结构）
- 向后兼容 apk_downloads（旧结构）
- 新增 `get_pc_game_path()` - 获取PC版路径
- 新增 `get_pc_executable()` - 获取PC版启动器
- 新增 `list_available_apks()` - 列出所有APK

**测试结果**:
```
可用APK文件:
  - com.minitech.miniworld.uc.apk (1609.4 MB) [packs_downloads]

PC版游戏:
  路径: .../miniworldPC_CN
  启动器: .../MicroMiniNew.exe
```

---

### 步骤 2: 创建双端反编译脚本

**文件**: `decompile_both_platforms.py`

**功能**:
1. Android APK反编译（apktool + jadx）
2. PC版文件分析
3. 双端对比分析

---

### 步骤 3: 执行双端反编译

#### Android端反编译 ✅

**APK信息**:
- 文件名: com.minitech.miniworld.uc.apk
- 大小: 1609.4 MB
- 包名: com.minitech.miniworld.uc
- 渠道: UC/九游

**反编译结果**:
- ✅ apktool完成（27秒）
- ✅ jadx完成（10秒）
- ✅ smali文件数: 5个（主要代码）
- ✅ 输出目录: `decompiled/android/`

**目录结构**:
```
decompiled/android/
├── AndroidManifest.xml
├── smali/
├── res/
├── assets/
├── lib/
└── jadx_sources/
```

#### PC端分析 ✅

**PC版信息**:
- 路径: miniworldPC_CN/miniworldLauncher/
- 主程序: MicroMiniNew.exe

**分析结果**:
- ✅ 找到 11 个EXE文件
- ✅ 找到 98 个DLL文件
- ✅ 找到 18 个配置文件
- ✅ 找到 3 个日志文件

**关键文件**:
```
EXE文件:
- MicroMiniNew.exe（主启动器）
- MiniGameApp.exe（游戏主程序）
- iworldpc.exe
- minigameapppc.exe
- ACE-Helper.exe（反作弊）

DLL文件:
- MiniGameAppBase.dll（游戏基础库）
- SkinUI.dll（UI库）
- node.dll（Node.js运行时）
- 98个其他DLL

配置文件:
- GameBabyConfig.dat
- settings.dat
- session.json
```

#### 对比分析 ✅

**平台对比**:
| 项目 | Android | PC |
|------|---------|-----|
| 包名 | com.minitech.miniworld.uc | - |
| 渠道 | UC/九游 | 官方 |
| 主程序 | APK | MiniGameApp.exe |
| 反作弊 | - | ACE-Helper.exe |

---

### 关键发现

#### 1. Android APK是UC渠道服
- 包名: `com.minitech.miniworld.uc`
- 不是官服（官服应为 `com.minitech.miniworld`）
- 可能包含UC SDK和定制协议

#### 2. PC版包含反作弊系统
- ACE-Helper.exe（腾讯ACE反作弊）
- 可能影响协议分析和调试

#### 3. PC版使用Node.js
- 包含 node.dll
- 可能使用JavaScript/TypeScript开发部分功能

#### 4. 双端可能使用不同协议
- Android: Java/Kotlin + UC SDK
- PC: C++/Node.js混合

---

### 输出文件

**反编译输出**:
```
MnMCPResources/packs_downloads/decompiled/
├── android/                    # Android反编译
│   ├── AndroidManifest.xml
│   ├── smali/
│   ├── jadx_sources/
│   └── ...
├── pc/                         # PC分析
│   ├── directory_structure.txt
│   ├── key_files.json
│   └── log_analysis.txt
└── comparison/                 # 对比分析
    └── platform_comparison.json
```

**项目文件**:
- `path_resolver.py` - 更新路径解析
- `decompile_both_platforms.py` - 双端反编译脚本
- `reverse_engineering/both_decompile_checkpoint.json` - 检查点

---

### 下一步建议

#### 立即可做
1. **分析Android smali代码**
   - 查找网络协议相关类
   - 提取UC SDK接口

2. **分析PC版DLL**
   - 使用IDA/Ghidra反编译MiniGameAppBase.dll
   - 查找网络通信函数

3. **对比双端协议**
   - 使用Wireshark抓包
   - 对比Android和PC的网络流量

#### 等待游戏更新完成后
1. **启动PC版游戏**
   - 注册账号
   - 进行联机测试

2. **使用Frida动态分析**
   - Hook网络函数
   - 实时查看数据包

---

### 注意事项

⚠️ **UC渠道服问题**:
- 当前APK是UC渠道服，不是官服
- 协议可能有UC定制
- 建议仍然下载官服APK进行对比

⚠️ **反作弊系统**:
- PC版包含ACE反作弊
- 可能检测调试器和Hook
- 需要谨慎进行动态分析

---
Made with ❤️ by ZCNotFound for cross-platform gaming
