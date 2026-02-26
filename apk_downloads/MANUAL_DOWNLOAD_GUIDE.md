# APK 手动下载指南

由于APK下载涉及版权保护和反爬虫机制，建议手动下载以下APK文件。

---

## 1. 迷你世界国服 1.53.1

### 官方下载方式
1. **访问官网**
   - 网址: https://www.mini1.cn/
   - 点击页面上的"安卓下载"按钮

2. **直接下载链接**
   ```
   https://app.mini1.cn/export/down_app/1
   ```

3. **应用商店下载**
   - 华为应用市场
   - 小米应用商店
   - OPPO/vivo应用商店
   - 搜索"迷你世界"

4. **保存文件名**
   ```
   miniworld_cn_1.53.1.apk
   ```

### 验证文件
- **包名**: com.minitech.miniworld
- **版本**: 1.53.1
- **大小**: 约 1.3GB

---

## 2. MiniWorld: Creata 1.7.15 (外服)

### APKPure下载
1. **访问APKPure**
   - 网址: https://apkpure.net/mini-world-creata/com.playmini.miniworld

2. **选择版本**
   - 在版本列表中找到 1.7.15
   - 点击"下载APK"

3. **备用下载源**
   - Uptodown: https://mini-world-creata.en.uptodown.com/android
   - Aptoide: https://mini-world-creata.en.aptoide.com/

4. **保存文件名**
   ```
   miniworld_en_1.7.15.apk
   ```

### 验证文件
- **包名**: com.playmini.miniworld
- **版本**: 1.7.15
- **大小**: 约 1.2GB

---

## 3. Minecraft Bedrock 1.20.60

### 正版购买下载
1. **Google Play Store**
   - 需要Google账号
   - 购买并下载游戏
   - 使用APK提取工具获取APK

2. **APK提取方法**
   - 使用 [APK Extractor](https://play.google.com/store/apps/details?id=com.ext.ui) 应用
   - 或使用 ADB 命令:
     ```bash
     adb shell pm path com.mojang.minecraftpe
     adb pull /data/app/.../base.apk minecraft_bedrock.apk
     ```

3. **保存文件名**
   ```
   minecraft_bedrock_1.20.60.apk
   ```

### 验证文件
- **包名**: com.mojang.minecraftpe
- **版本**: 1.20.60.x
- **大小**: 约 200MB

---

## 下载后验证

### 检查APK完整性
```bash
# 使用apktool验证
apktool d miniworld_cn_1.53.1.apk -o test_decode

# 检查AndroidManifest.xml
# 确认包名和版本号
```

### 查看APK信息
```bash
# 使用aapt（Android SDK工具）
aapt dump badging miniworld_cn_1.53.1.apk

# 或使用Python
python -c "
import zipfile
with zipfile.ZipFile('miniworld_cn_1.53.1.apk') as z:
    print('APK内容:')
    for name in z.namelist()[:20]:
        print(f'  {name}')
"
```

---

## 反编译准备

下载完成后，使用以下工具进行反编译：

### 1. 使用 apktool 反编译
```bash
# 反编译迷你世界国服
apktool d miniworld_cn_1.53.1.apk -o miniworld_cn_decompiled

# 反编译迷你世界外服
apktool d miniworld_en_1.7.15.apk -o miniworld_en_decompiled

# 反编译Minecraft基岩版
apktool d minecraft_bedrock_1.20.60.apk -o mc_bedrock_decompiled
```

### 2. 使用 jadx 查看源代码
```bash
# 启动jadx GUI
..\tools\jadx\bin\jadx-gui.bat miniworld_cn_1.53.1.apk
```

### 3. 使用 frida 动态分析
```bash
# 解压frida-server
7z x ..\tools\frida-server.xz

# 推送到Android设备
adb push frida-server /data/local/tmp/
adb shell "chmod +x /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"
```

---

## 目录结构

下载完成后，目录结构应为：
```
apk_downloads/
├── miniworld_cn_1.53.1.apk          # 迷你世界国服
├── miniworld_en_1.7.15.apk          # MiniWorld: Creata外服
├── minecraft_bedrock_1.20.60.apk    # Minecraft基岩版
├── miniworld_cn_decompiled/         # 反编译后的国服
├── miniworld_en_decompiled/         # 反编译后的外服
├── mc_bedrock_decompiled/           # 反编译后的MC基岩版
├── download_apk.py                  # 自动下载脚本
├── MANUAL_DOWNLOAD_GUIDE.md         # 本文件
└── README.md                        # 目录说明
```

---

## 注意事项

1. **版权问题**
   - 仅用于逆向工程研究
   - 不得传播或商业使用
   - 24小时内删除

2. **文件大小**
   - 确保有足够的存储空间（约5GB）
   - 使用稳定的网络连接

3. **安全提示**
   - 只从官方渠道下载
   - 下载后验证文件哈希
   - 使用虚拟机或沙盒环境分析

---

## 下一步

下载完成后，继续执行：
1. [反编译APK](DECOMPILE_GUIDE.md)
2. [协议分析](../docs/PROTOCOL_ANALYSIS.md)
3. [动态调试](../docs/DYNAMIC_ANALYSIS.md)

---
Made with ❤️ by ZCNotFound for cross-platform gaming
