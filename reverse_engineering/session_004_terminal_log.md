# 逆向工程会话记录 - Session 004
## 任务: 检测状态、移动大文件、执行APK反编译
## 开始时间: 2026-02-26 00:32
## 完成时间: 2026-02-26 00:45

### 步骤 1: 创建外部资源目录
```powershell
New-Item -ItemType Directory -Force -Path 'C:\Users\Sails\Documents\Coding\MnMCPResources'
New-Item -ItemType Directory -Force -Path 'C:\Users\Sails\Documents\Coding\MnMCPResources\server'
New-Item -ItemType Directory -Force -Path 'C:\Users\Sails\Documents\Coding\MnMCPResources\tools'
New-Item -ItemType Directory -Force -Path 'C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads'
```
状态: ✅ 完成

### 步骤 2: 扫描并移动大文件

创建了 `move_large_files.py` 脚本，移动超过100MB的文件到外部目录。

执行结果:
```
[发现大文件] apk_downloads\miniworld_cn_latest.apk
  移动: miniworld_cn_latest.apk
    大小: 1.60 GB
    到: C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_latest.apk
    创建位置记录文件: ✓
```

**重要发现**: APK文件已经存在！
- 文件: miniworld_cn_latest.apk
- 大小: 1.60 GB
- 已移动到外部资源目录

### 步骤 3: 重命名APK文件

将下载的APK文件重命名为规范名称：
```
miniworld_cn_latest.apk → miniworld_cn_1.53.1.apk
```
状态: ✅ 完成

### 步骤 4: 创建专用反编译脚本

创建了 `decompile_miniworld_cn.py` 脚本，专门用于反编译迷你世界国服APK。

脚本功能：
- 自动检测APK文件
- 检查反编译工具
- 使用apktool反编译（资源和smali）
- 使用jadx反编译（Java源代码）
- 分析目录结构
- 搜索关键协议文件

### 步骤 5: 启动反编译（后台运行）

由于反编译1.6GB的APK需要较长时间（预计10-30分钟），已在后台启动：
```bash
python decompile_miniworld_cn.py
```

日志文件: `C:\Users\Sails\Documents\python_7808.log`

### 当前状态

#### 已准备
- ✅ 外部资源目录 (MnMCPResources/)
- ✅ 大文件移动脚本
- ✅ 迷你世界国服APK (1.60 GB)
- ✅ 反编译脚本
- ⏳ 反编译进行中（后台）

#### 目录结构
```
MnMCPResources/                          # 外部资源目录
└── apk_downloads/
    └── miniworld_cn_1.53.1.apk         # 迷你世界国服APK (1.60 GB)

Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── apk_downloads/
│   ├── miniworld_cn_1.53.1.apk.location  # 位置记录文件
│   ├── decompile_miniworld_cn.py         # 专用反编译脚本
│   ├── download_apk.py
│   ├── decompile_apk.py
│   ├── MANUAL_DOWNLOAD_GUIDE.md
│   └── DECOMPILE_GUIDE.md
├── tools/                                 # 工具目录
├── server/                                # 服务端目录
├── reverse_engineering/                   # 会话记录
│   └── session_004_terminal_log.md
├── move_large_files.py                    # 大文件移动脚本
└── EXTERNAL_RESOURCES.md                  # 外部资源说明
```

### 下一步操作

1. **等待反编译完成**
   - 监控日志: `Get-Content C:\Users\Sails\Documents\python_7808.log -Wait`
   - 预计时间: 10-30分钟

2. **反编译完成后分析**
   ```bash
   # 查看输出目录
   dir C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_decompiled\
   
   # 使用jadx GUI查看
   ..\tools\jadx\bin\jadx-gui.bat C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_1.53.1.apk
   ```

3. **搜索协议相关代码**
   ```bash
   # 搜索网络相关
   grep -r "socket" miniworld_cn_decompiled/smali/ --include="*.smali"
   
   # 搜索加密相关
   grep -r "encrypt\|AES\|RSA" miniworld_cn_decompiled/smali/ --include="*.smali"
   ```

### 断点记录
- 当前步骤: APK反编译进行中（后台）
- 等待: 反编译完成
- 下次继续: 分析反编译结果，提取协议信息
- 备份位置: backups/session_004_backup.zip

### 生成的文件

| 文件 | 用途 | 位置 |
|------|------|------|
| move_large_files.py | 大文件移动脚本 | 项目根目录 |
| EXTERNAL_RESOURCES.md | 外部资源说明 | 项目根目录 |
| decompile_miniworld_cn.py | 专用反编译脚本 | apk_downloads/ |
| miniworld_cn_1.53.1.apk | 迷你世界国服APK | MnMCPResources/ |

---
Made with ❤️ by ZCNotFound for cross-platform gaming
