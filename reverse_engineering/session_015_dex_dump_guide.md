# 逆向工程会话记录 - Session 015
## 任务：BlackDex脱壳指南 + 推进其他任务
## 日期：2026-02-26
## 状态：进行中

---

## 一、BlackDex脱壳产出说明

### 会产出什么？

BlackDex脱壳后会在设备上生成以下文件：

```
/sdcard/Download/BlackDex/
└── com.minitech.miniworld/              # 包名目录
    ├── dump_0.dex                       # 主DEX文件（10-50MB）
    ├── dump_1.dex                       # 附加DEX文件（10-50MB）
    ├── dump_2.dex                       # 可能有多个...
    └── ...                              # 总共3-10个DEX文件
```

**预期总大小**：50MB - 150MB

**成功标志**：
- ✅ 多个 `dump_*.dex` 文件
- ✅ 总大小 > 50MB
- ✅ 单个文件 > 10MB

---

## 二、你需要复制什么到资源文件夹

### 必须复制的内容

**整个脱壳输出目录**：

```
MnMCPResources/
└── packs_downloads/
    └── dumped_dex/                              # 新建目录
        └── com.minitech.miniworld/              # 整个目录复制
            ├── dump_0.dex                       # 必须
            ├── dump_1.dex                       # 必须
            ├── dump_2.dex                       # 必须
            └── ...                              # 所有DEX文件
```

### 复制步骤

#### 方法1：使用ADB（推荐）
```bash
# 在电脑上执行
adb pull /sdcard/Download/BlackDex/com.minitech.miniworld "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\"
```

#### 方法2：使用文件管理器
1. 在设备上打开文件管理器
2. 找到 `/sdcard/Download/BlackDex/com.minitech.miniworld/`
3. 将整个目录压缩为ZIP
4. 发送到电脑
5. 解压到 `MnMCPResources/packs_downloads/dumped_dex/`

---

## 三、复制后的自动处理

### 运行处理工具
```bash
cd "C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\android_shell"
python process_dumped_dex.py
```

### 工具会自动完成
1. ✅ 检查所有DEX文件
2. ✅ 使用jadx反编译
3. ✅ 分析关键类（网络/协议/加密/登录）
4. ✅ 生成分析报告

### 产出位置
- **反编译源码**：`dumped_dex/com.minitech.miniworld/sources/`
- **分析报告**：`dumped_dex/com.minitech.miniworld/analysis/ANALYSIS_REPORT.md`

---

## 四、同时推进的其他任务

### 🟡 任务1：PC端抓包准备
**状态**：⬜ 待执行
**阻塞**：无（可并行）

**操作步骤**：
```bash
# 1. 运行抓包准备工具
cd tools/pc_capture/
python pc_network_capture.py

# 2. 安装Proxifier（如果没有）
# 下载：https://www.proxifier.com/

# 3. 安装Wireshark（如果没有）
# 下载：https://www.wireshark.org/download.html
```

**产出**：
- Proxifier配置文件
- Wireshark过滤规则
- 抓包操作指南

### 🟡 任务2：注册第二个测试账号
**状态**：⬜ 待执行
**阻塞**：无（可并行）

**操作步骤**：
1. 访问 https://www.mini1.cn/
2. 点击注册
3. 使用另一个手机号注册
4. 记录迷你号和密码
5. 更新 `setup/test_accounts.md`

### 🟡 任务3：下载外服APK
**状态**：⬜ 待执行
**阻塞**：无（可并行）

**操作步骤**：
1. 访问 https://apkpure.net/mini-world-creata/com.playmini.miniworld
2. 找到版本 1.7.15
3. 下载APK
4. 保存为 `miniworld_en_1.7.15.apk`
5. 放置到 `MnMCPResources/packs_downloads/`

---

## 五、任务优先级建议

### 立即执行（今天）
1. 🔄 **等待BlackDex完成**（正在进行）
2. ⬜ **复制脱壳产出到电脑**
3. ⬜ **运行自动处理工具**

### 今天或明天
4. ⬜ **安装Proxifier和Wireshark**
5. ⬜ **运行PC端抓包准备工具**
6. ⬜ **注册第二个测试账号**

### 本周内
7. ⬜ **分析脱壳后的代码**（识别网络协议类）
8. ⬜ **执行PC端抓包**
9. ⬜ **下载外服APK**

---

## 六、检查点

### 检查点1：DEX文件复制完成
**标准**：`MnMCPResources/packs_downloads/dumped_dex/com.minitech.miniworld/` 存在且包含DEX文件
**验证**：运行 `process_dumped_dex.py` 能检测到文件

### 检查点2：自动处理完成
**标准**：生成分析报告 `analysis/ANALYSIS_REPORT.md`
**验证**：报告包含网络类、协议类、加密类列表

### 检查点3：关键类识别
**标准**：找到至少3个网络通信相关类
**验证**：能定位到Socket连接、数据包发送代码

---

## 七、已创建的文档和工具

| 文件 | 用途 |
|------|------|
| `docs/BlackDex_Output_Guide.md` | 完整的脱壳产出指南 |
| `tools/android_shell/process_dumped_dex.py` | 自动处理DEX文件 |
| `QUICK_ACTION.md` | 快速操作参考 |

---

## 八、下一步立即执行

1. ⏳ **等待BlackDex完成**
2. 📋 **复制DEX文件到电脑**：
   ```bash
   adb pull /sdcard/Download/BlackDex/com.minitech.miniworld "C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\dumped_dex\"
   ```
3. 🚀 **运行自动处理工具**：
   ```bash
   cd tools/android_shell/
   python process_dumped_dex.py
   ```

同时可以并行执行：
- 安装Proxifier和Wireshark
- 注册第二个测试账号
- 下载外服APK

---

**祝脱壳顺利！🎉**
