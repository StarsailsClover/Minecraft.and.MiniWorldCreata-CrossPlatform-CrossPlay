# BlackDex脱壳产出指南

## BlackDex脱壳会产出什么？

当你使用BlackDex对迷你世界APK进行脱壳时，会产出以下文件：

### 1. 主要产出文件

#### DEX文件（核心）
```
/sdcard/Download/BlackDex/
└── com.minitech.miniworld/           # 包名目录
    ├── dump_0.dex                    # 第一个DEX文件（主程序）
    ├── dump_1.dex                    # 第二个DEX文件
    ├── dump_2.dex                    # 可能有多个DEX...
    └── ...
```

**预期文件大小**：
- 总大小：50MB - 150MB（取决于加固方式）
- 单个DEX：10MB - 50MB
- 文件数量：3-10个DEX文件

**注意**：如果只有1-2个DEX文件，或总大小小于50MB，可能脱壳不完整

#### 其他可能产出
```
com.minitech.miniworld/
├── classes.dex                       # 某些版本会合并输出
├── lib/                              # SO库文件（可选）
└── assets/                           # 资源文件（可选）
```

### 2. 如何验证脱壳成功

#### 检查文件大小
```bash
# 在设备的终端中执行
ls -lh /sdcard/Download/BlackDex/com.minitech.miniworld/

# 成功的标志：
# - 有多个dump_*.dex文件
# - 总大小 > 50MB
# - 单个文件 > 10MB
```

#### 检查DEX内容
```bash
# 使用dexdump检查
dexdump -l /sdcard/Download/BlackDex/com.minitech.miniworld/dump_0.dex | head -20

# 应该看到大量类名，如：
# com.minitech.miniworld.activities.MainActivity
# com.minitech.miniworld.network.NetworkManager
# com.minitech.miniworld.protocol.PacketHandler
```

---

## 你应该把什么放到资源文件夹里？

### 必须复制的内容

**整个脱壳输出目录**：
```
MnMCPResources/
└── packs_downloads/
    └── dumped_dex/                              # 新建目录
        └── com.minitech.miniworld/              # 整个目录复制过来
            ├── dump_0.dex                       # 必须
            ├── dump_1.dex                       # 必须
            ├── dump_2.dex                       # 必须
            └── ...                              # 所有DEX文件
```

### 复制步骤

#### 方法1：使用ADB（推荐）
```bash
# 1. 在电脑上执行，创建目标目录
mkdir -p "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex"

# 2. 从设备复制整个脱壳目录
adb pull /sdcard/Download/BlackDex/com.minitech.miniworld "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\"

# 3. 验证复制结果
dir "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\com.minitech.miniworld\"
```

#### 方法2：使用文件管理器
1. 在设备上打开文件管理器
2. 找到 `/sdcard/Download/BlackDex/com.minitech.miniworld/`
3. 将整个目录压缩为ZIP文件
4. 通过USB、微信、QQ等方式发送到电脑
5. 在电脑上解压到 `MnMCPResources/packs_downloads/dumped_dex/`

---

## 复制后的验证清单

复制完成后，检查以下内容：

```bash
# 检查清单
[✓] DEX文件存在且大小合理（> 10MB each）
[✓] 文件数量 >= 3个
[✓] 总大小 > 50MB
[✓] 文件名格式：dump_0.dex, dump_1.dex, ...
[✓] 目录结构正确
```

---

## 下一步：反编译DEX

复制到资源文件夹后，使用jadx反编译：

### 使用自动处理工具（推荐）
```bash
# 在项目目录执行
cd tools/android_shell/
python process_dumped_dex.py

# 这个工具会自动：
# 1. 检查所有DEX文件
# 2. 使用jadx反编译
# 3. 分析关键类
# 4. 生成分析报告
```

### 手动反编译
```bash
# 使用jadx GUI查看
tools\jadx\bin\jadx-gui.bat

# 然后打开：
# C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\com.minitech.miniworld\dump_0.dex
```

---

## 预期反编译结果

成功的反编译应该产出：

```
dumped_dex/com.minitech.miniworld/sources/
├── com/
│   ├── minitech/
│   │   └── miniworld/              # 游戏主包
│   │       ├── activities/         # Activity类
│   │       ├── network/            # 网络通信（关键！）
│   │       ├── protocol/           # 协议定义（关键！）
│   │       ├── game/               # 游戏逻辑
│   │       └── utils/              # 工具类
│   └── tencent/                    # 腾讯SDK
│       └── ...
├── android/                        # Android框架
└── ...                             # 其他依赖库
```

---

## 关键文件查找

反编译后，重点关注以下类：

```java
// 网络通信相关
com.minitech.miniworld.network.*
com.minitech.miniworld.net.*
com.minitech.miniworld.socket.*

// 协议处理相关
com.minitech.miniworld.protocol.*
com.minitech.miniworld.packet.*
com.minitech.miniworld.message.*

// 加密相关
com.minitech.miniworld.crypto.*
com.minitech.miniworld.encrypt.*
com.minitech.miniworld.security.*

// 登录认证相关
com.minitech.miniworld.login.*
com.minitech.miniworld.auth.*
com.minitech.miniworld.account.*
```

---

## 常见问题

### Q: 脱壳后DEX文件很小（< 5MB）？
**A**: 脱壳失败，可能原因：
- BlackDex版本不兼容
- 设备环境不对（需要特定Android版本）
- APK有额外的反脱壳机制

**解决**：尝试其他脱壳工具（Youpk、FDex2）

### Q: 反编译后代码混淆严重？
**A**: 正常情况，迷你世界使用了ProGuard混淆
- 类名可能是 a, b, c, d...
- 需要结合字符串搜索和动态分析
- 重点关注网络相关的字符串（"http", "socket", "tcp", "udp"）

### Q: 找不到网络相关代码？
**A**: 可能原因：
- DEX文件不完整（缺少部分dump文件）
- 网络代码在SO库中（C/C++层）
- 使用了第三方网络库（OkHttp, Netty等）

**解决**：检查所有DEX文件，搜索网络库相关类

---

## 快速检查命令

脱壳完成后，在设备上使用以下命令快速验证：

```bash
# 1. 检查文件大小
ls -lh /sdcard/Download/BlackDex/com.minitech.miniworld/

# 2. 统计DEX数量
ls /sdcard/Download/BlackDex/com.minitech.miniworld/*.dex | wc -l

# 3. 查看DEX中的类数量
dexdump -l /sdcard/Download/BlackDex/com.minitech.miniworld/dump_0.dex | grep "Class descriptor" | wc -l
# 应该看到数千个类

# 4. 搜索关键字符串
strings /sdcard/Download/BlackDex/com.minitech.miniworld/dump_0.dex | grep -i "protocol\|socket\|network" | head -10
```

---

## 总结

### 你需要做的：

1. **在BlackDex上脱壳** ✅（进行中）
2. **复制产出到资源文件夹**：
   ```
   MnMCPResources/packs_downloads/dumped_dex/com.minitech.miniworld/
   ```
3. **运行自动处理工具**：
   ```bash
   cd tools/android_shell/
   python process_dumped_dex.py
   ```
4. **查看分析报告**，识别关键网络类

### 预期时间：
- 脱壳：5-10分钟
- 复制文件：2-5分钟
- 自动处理：10-30分钟
- 初步分析：1-2小时

祝脱壳顺利！🎉
