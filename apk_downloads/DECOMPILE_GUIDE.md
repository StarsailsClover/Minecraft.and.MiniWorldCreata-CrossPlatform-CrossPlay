# APK反编译指南

本指南介绍如何使用apktool和jadx反编译APK文件，提取协议相关信息。

---

## 工具准备

确保以下工具已安装：
- `tools/apktool.jar` - APK反编译工具
- `tools/jadx/` - Java反编译器
- Java 8+ 运行环境

---

## 快速开始

### 1. 自动反编译

```bash
# 反编译所有APK
python decompile_apk.py all

# 反编译特定APK
python decompile_apk.py miniworld_cn
python decompile_apk.py miniworld_en
python decompile_apk.py minecraft_bedrock

# 使用jadx GUI打开
python decompile_apk.py miniworld_cn --gui
```

### 2. 手动反编译

#### 使用apktool

```bash
# 反编译APK（提取资源和smali代码）
java -jar ..\tools\apktool.jar d miniworld_cn_1.53.1.apk -o miniworld_cn_decompiled

# 参数说明
# d - decode（反编译）
# -o - 输出目录
# -f - 强制覆盖
# -s - 不反编译dex（只提取资源）
# -r - 不反编译资源（只反编译代码）
```

#### 使用jadx

```bash
# 命令行反编译（提取Java源代码）
..\tools\jadx\bin\jadx.bat -d miniworld_cn_sources --show-bad-code miniworld_cn_1.53.1.apk

# GUI模式（推荐用于分析）
..\tools\jadx\bin\jadx-gui.bat miniworld_cn_1.53.1.apk
```

---

## 反编译输出结构

### apktool输出
```
miniworld_cn_decompiled/
├── AndroidManifest.xml    # 应用配置（包含权限、组件声明）
├── apktool.yml           # 反编译配置
├── assets/               # 资源文件
├── lib/                  # 原生库(.so文件)
├── original/             # 原始文件
├── res/                  # 资源文件（布局、字符串等）
├── smali/                # Dalvik字节码（关键！）
│   ├── com/
│   │   └── minitech/
│   │       └── miniworld/
│   │           ├── network/      # 网络相关代码
│   │           ├── protocol/     # 协议实现
│   │           ├── encryption/   # 加密算法
│   │           └── ...
│   └── ...
└── unknown/              # 未知文件
```

### jadx输出
```
miniworld_cn_sources/
├── sources/              # Java源代码
│   └── com/
│       └── minitech/
│           └── miniworld/
│               ├── MainActivity.java
│               ├── network/
│               │   ├── NetworkManager.java
│               │   ├── PacketHandler.java
│               │   └── ...
│               ├── protocol/
│               │   ├── Protocol.java
│               │   ├── Packet.java
│               │   └── ...
│               └── ...
└── resources/            # 资源文件
```

---

## 关键分析目标

### 1. 网络协议相关

查找以下关键词：
```
- socket
- tcp
- udp
- http
- ssl
- protocol
- packet
- message
- encrypt
- decrypt
- aes
- rsa
```

#### 使用grep搜索
```bash
# 在smali代码中搜索网络相关类
grep -r "socket" miniworld_cn_decompiled/smali/ --include="*.smali"

# 搜索加密相关
grep -r "encrypt\|decrypt\|AES\|RSA" miniworld_cn_decompiled/smali/ --include="*.smali"

# 搜索协议相关
grep -r "protocol\|packet\|message" miniworld_cn_decompiled/smali/ --include="*.smali"
```

### 2. 登录认证流程

重点关注：
- `LoginActivity` / `LoginManager`
- `AuthManager` / `Authentication`
- `SessionManager`
- `TokenManager`

### 3. 数据包结构

查找：
- `Packet` / `Message` / `Data` 类
- 序列化/反序列化方法
- 字段定义（id, type, length, data等）

### 4. 加密算法

查找：
- `AES` / `RSA` / `DES` 实现
- `Cipher` 类使用
- 密钥生成和管理
- 初始化向量(IV)处理

---

## 分析技巧

### 1. 从入口开始

```bash
# 查看AndroidManifest.xml找到主Activity
cat miniworld_cn_decompiled/AndroidManifest.xml | grep "MAIN"

# 通常格式：
# <activity android:name=".MainActivity">
#     <intent-filter>
#         <action android:name="android.intent.action.MAIN"/>
#         <category android:name="android.intent.category.LAUNCHER"/>
#     </intent-filter>
# </activity>
```

### 2. 追踪网络请求

```bash
# 在smali中查找URL或IP
grep -r "http\|https\|\\d\\+\\.\\d\\+\\.\\d\\+\\.\\d\\+" miniworld_cn_decompiled/smali/ --include="*.smali"

# 查找端口号
grep -r ":[0-9]\\+" miniworld_cn_decompiled/smali/ --include="*.smali"
```

### 3. 使用jadx搜索

在jadx GUI中：
1. 打开APK文件
2. 使用 `Ctrl+Shift+F` 全局搜索
3. 输入关键词如 "socket", "encrypt", "protocol"
4. 分析搜索结果

### 4. 对比分析

```bash
# 对比国服和外服的差异
diff -r miniworld_cn_decompiled/smali/com/minitech/miniworld/network/ \
         miniworld_en_decompiled/smali/com/minitech/miniworld/network/

# 找出不同的文件
diff -qr miniworld_cn_decompiled/smali/ miniworld_en_decompiled/smali/ | grep "differ"
```

---

## 常见问题

### 1. 反编译失败

**问题**: apktool报错 `Exception in thread "main" brut.androlib.AndrolibException`

**解决**:
```bash
# 更新apktool框架
java -jar apktool.jar empty-framework-dir --force

# 重新反编译
java -jar apktool.jar d miniworld_cn_1.53.1.apk -o miniworld_cn_decompiled -f
```

### 2. 内存不足

**问题**: jadx反编译时内存溢出

**解决**:
```bash
# 增加内存分配
set JAVA_OPTS=-Xmx4G
..\tools\jadx\bin\jadx.bat -J-Xmx4G -d output_dir apk_file.apk
```

### 3. 代码混淆

**问题**: 类名被混淆为a, b, c等

**解决**:
- 使用jadx的反混淆功能
- 查找字符串常量（通常未加密）
- 分析代码逻辑推断功能
- 结合动态调试(frida)确定功能

---

## 下一步

反编译完成后：
1. [协议分析](../docs/PROTOCOL_ANALYSIS.md) - 分析网络协议
2. [动态调试](../docs/DYNAMIC_ANALYSIS.md) - 使用frida动态分析
3. [数据包捕获](../docs/PACKET_CAPTURE.md) - 抓取真实数据包

---
Made with ❤️ by ZCNotFound for cross-platform gaming
