# 逆向工程会话记录 - Session 003
## 任务: 下载 APK 文件并反编译分析
## 开始时间: 2026-02-26 00:00
## 完成时间: 2026-02-26 00:15

### 步骤 1: 搜索APK下载源

#### 迷你世界国服
- 官网: https://www.mini1.cn/
- 下载链接: https://app.mini1.cn/export/down_app/1
- 版本: 1.53.1
- 包名: com.minitech.miniworld
- 大小: 约1.3GB

#### MiniWorld: Creata (外服)
- APKPure: https://apkpure.net/mini-world-creata/com.playmini.miniworld
- 版本: 1.7.15
- 包名: com.playmini.miniworld
- 大小: 约1.2GB

#### Minecraft Bedrock
- Google Play Store (需购买)
- 版本: 1.20.60
- 包名: com.mojang.minecraftpe
- 大小: 约200MB

### 步骤 2: 尝试自动下载

创建了 `download_apk.py` 脚本尝试自动下载：
```bash
python download_apk.py
```

结果:
- 迷你世界国服: ❌ HTTP 567 / SSL错误
- MiniWorld外服: ❌ HTTP 403 Forbidden
- Minecraft: ⚠️ 需要正版购买

### 步骤 3: 创建手动下载指南

由于APK下载涉及：
1. 反爬虫机制
2. 验证码保护
3. 版权保护
4. 重定向机制

创建了详细的手动下载指南：
- `MANUAL_DOWNLOAD_GUIDE.md` - APK手动下载步骤
- `DECOMPILE_GUIDE.md` - 反编译操作指南

### 步骤 4: 创建反编译脚本

创建了 `decompile_apk.py` 自动化脚本：
```bash
# 反编译所有APK
python decompile_apk.py all

# 反编译特定APK
python decompile_apk.py miniworld_cn

# 使用GUI
python decompile_apk.py miniworld_cn --gui
```

功能：
- 自动检查工具
- 使用apktool反编译（资源和smali）
- 使用jadx反编译（Java源代码）
- 支持GUI模式
- 自动清理旧文件

### 步骤 5: 更新文档

#### 更新的文件
1. `apk_downloads/README.md` - 目录说明
2. `apk_downloads/MANUAL_DOWNLOAD_GUIDE.md` - 手动下载指南
3. `apk_downloads/DECOMPILE_GUIDE.md` - 反编译指南
4. `apk_downloads/download_apk.py` - 自动下载脚本
5. `apk_downloads/decompile_apk.py` - 反编译脚本

#### 关键内容
- 官方下载链接
- 备用下载源
- 文件验证方法
- 反编译命令
- 分析技巧
- 常见问题解决

### 当前状态

#### 已准备
- ✅ 反编译工具 (apktool, jadx)
- ✅ 自动化脚本
- ✅ 详细文档
- ✅ 分析指南

#### 待完成（需要手动操作）
- ⬜ 下载迷你世界国服 APK
- ⬜ 下载 MiniWorld: Creata APK
- ⬜ 下载 Minecraft Bedrock APK
- ⬜ 执行反编译
- ⬜ 分析协议代码

### 下一步操作指南

1. **手动下载APK**
   ```
   访问 https://www.mini1.cn/
   点击"安卓下载"
   保存为 miniworld_cn_1.53.1.apk
   ```

2. **执行反编译**
   ```bash
   cd apk_downloads
   python decompile_apk.py all
   ```

3. **分析代码**
   ```bash
   # 搜索网络相关代码
   grep -r "socket" miniworld_cn_decompiled/smali/ --include="*.smali"
   
   # 使用jadx GUI
   ..\tools\jadx\bin\jadx-gui.bat miniworld_cn_1.53.1.apk
   ```

### 断点记录
- 当前步骤: APK下载脚本和指南创建完成
- 等待: 用户手动下载APK文件
- 下次继续: 执行反编译和协议分析
- 备份位置: backups/session_003_backup.zip

### 生成的文件清单

| 文件 | 用途 | 大小 |
|------|------|------|
| download_apk.py | 自动下载脚本 | ~5KB |
| decompile_apk.py | 反编译脚本 | ~8KB |
| MANUAL_DOWNLOAD_GUIDE.md | 手动下载指南 | ~8KB |
| DECOMPILE_GUIDE.md | 反编译指南 | ~10KB |
| README.md | 目录说明 | ~3KB |

---
Made with ❤️ by ZCNotFound for cross-platform gaming
