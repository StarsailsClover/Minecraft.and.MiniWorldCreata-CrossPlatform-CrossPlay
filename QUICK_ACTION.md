# 快速操作指南 - BlackDex脱壳后

## 🎯 你现在需要做的（按顺序）

### 1. 等待BlackDex完成 ⏳
- 在设备上观察BlackDex进度
- 预计时间：5-10分钟
- 完成标志：显示"脱壳完成"或有"dump_*.dex"文件

### 2. 复制DEX文件到电脑 📋

**使用ADB（推荐）**：
```bash
adb pull /sdcard/Download/BlackDex/com.minitech.miniworld "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\"
```

**或使用文件管理器**：
1. 找到 `/sdcard/Download/BlackDex/com.minitech.miniworld/`
2. 压缩为ZIP
3. 发送到电脑
4. 解压到 `MnMCPResources/packs_downloads/dumped_dex/`

### 3. 运行自动处理工具 🚀

```bash
cd "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\android_shell"
python process_dumped_dex.py
```

**这个工具会自动**：
- ✅ 检查DEX文件
- ✅ 反编译所有DEX
- ✅ 分析关键类（网络/协议/加密/登录）
- ✅ 生成分析报告

### 4. 查看结果 👀

**反编译源码**：
```
MnMCPResources/packs_downloads/dumped_dex/com.minitech.miniworld/sources/
```

**分析报告**：
```
MnMCPResources/packs_downloads/dumped_dex/com.minitech.miniworld/analysis/ANALYSIS_REPORT.md
```

---

## 📦 BlackDex会产出什么

### 主要文件
- **多个DEX文件**：`dump_0.dex`, `dump_1.dex`, ...
- **总大小**：50MB - 150MB
- **位置**：`/sdcard/Download/BlackDex/com.minitech.miniworld/`

### 你需要复制什么
✅ **整个 `com.minitech.miniworld` 目录**（包含所有DEX文件）

---

## 🔄 同时可以做的（并行）

### 安装抓包工具
1. **Proxifier**：https://www.proxifier.com/ （下载试用版）
2. **Wireshark**：https://www.wireshark.org/download.html （免费）

### 注册第二个测试账号
1. 访问 https://www.mini1.cn/
2. 注册新账号
3. 记录迷你号和密码
4. 更新 `setup/test_accounts.md`

### 下载外服APK
1. 访问 https://apkpure.net/mini-world-creata/com.playmini.miniworld
2. 下载版本 1.7.15
3. 保存到 `MnMCPResources/packs_downloads/miniworld_en_1.7.15.apk`

---

## 📊 预期产出时间表

| 时间 | 任务 | 产出 |
|------|------|------|
| +10分钟 | BlackDex完成 | DEX文件（50-150MB） |
| +15分钟 | 复制到电脑 | `dumped_dex/` 目录 |
| +30分钟 | 自动处理 | 反编译源码 + 分析报告 |
| +1小时 | 初步分析 | 识别关键网络类 |
| +2小时 | PC抓包准备 | Proxifier配置 + Wireshark规则 |
| +1天 | 完整分析 | 协议结构初稿 |

---

## ⚠️ 如果出现问题

### BlackDex脱壳失败
- 尝试 Youpk：https://github.com/Youlor/Youpk
- 尝试 FDex2
- 或转向PC端抓包分析

### DEX文件太小（< 10MB）
- 脱壳不完整，尝试其他工具
- 可能使用了SO库（需要分析.so文件）

### 反编译出错
- 使用 `jadx-gui` 手动查看
- 某些DEX可能损坏，尝试其他DEX文件

---

**祝脱壳顺利！🎉**
