# APK下载目录

本目录用于存放逆向工程所需的APK文件。

## 需要的APK文件

### 1. Minecraft Bedrock (基岩版)
- **版本**: 1.20.6 (或接近版本)
- **包名**: com.mojang.minecraftpe
- **用途**: 分析基岩版协议
- **来源**: 
  - Google Play Store (需要购买)
  - 官方渠道: https://www.minecraft.net/
- **注意**: 需要正版授权

### 2. 迷你世界国服
- **版本**: 1.53.1
- **包名**: com.minitech.miniworld
- **用途**: 分析国服协议
- **来源**:
  - 官网: https://www.mini1.cn/
  - 应用商店: 华为/小米/OPPO/vivo应用商店
- **下载方式**: 官网直接下载

### 3. MiniWorld: Creata (外服)
- **版本**: 1.7.15
- **包名**: com.playmini.miniworld
- **用途**: 分析外服协议
- **来源**:
  - Google Play Store
  - APKPure: https://apkpure.net/mini-world-creata/com.playmini.miniworld
- **注意**: 海外版本

## 手动下载步骤

### 迷你世界国服
1. 访问 https://www.mini1.cn/
2. 点击"下载游戏"
3. 选择Android版本
4. 保存到本目录

### MiniWorld: Creata
1. 访问 https://apkpure.net/mini-world-creata/com.playmini.miniworld
2. 找到版本 1.7.15
3. 点击下载APK
4. 保存到本目录

### Minecraft Bedrock
1. 购买正版: https://www.minecraft.net/store/minecraft-bedrock-edition
2. 从Google Play下载
3. 或使用已购买的账号下载APK

## 文件命名规范
```
miniworld_cn_1.53.1.apk          # 迷你世界国服
miniworld_en_1.7.15.apk          # MiniWorld: Creata外服
minecraft_bedrock_1.20.6.apk     # Minecraft基岩版
```

## 下一步
下载完成后，使用apktool进行反编译:
```bash
apktool d miniworld_cn_1.53.1.apk -o miniworld_cn_decompiled
apktool d miniworld_en_1.7.15.apk -o miniworld_en_decompiled
apktool d minecraft_bedrock_1.20.6.apk -o mc_bedrock_decompiled
```

---
Made with ❤️ by ZCNotFound for cross-platform gaming
