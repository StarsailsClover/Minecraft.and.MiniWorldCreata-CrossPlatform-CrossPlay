# 逆向工程会话记录 - Session 015
## 任务: BlackDex脱壳进行中 + 推进其他任务
## 日期: 2026-02-26
## 状态: 进行中

---

## 一、当前进展

### 🔴 主线任务: Android端脱壳
**状态**: 🔄 进行中（BlackDex正在运行）

**用户操作**:
- ✅ 已将APK放到Root设备上的BlackDex
- ✅ BlackDex正在脱壳处理中

**预期产出**:
- 多个DEX文件（dump_0.dex, dump_1.dex, ...）
- 总大小: 50MB - 150MB
- 文件位置: `/sdcard/Download/BlackDex/com.minitech.miniworld/`

---

## 二、已完成的准备工作

### 1. 创建BlackDex产出指南
**文件**: `docs/BlackDex_Output_Guide.md`

**内容**:
- 脱壳产出说明
- 文件复制指南
- 反编译步骤
- 关键类查找方法

### 2. 创建DEX处理工具
**文件**: `tools/android_shell/process_dumped_dex.py`

**功能**:
- 自动检查脱壳文件
- 使用jadx反编译所有DEX
- 自动分析关键类（网络/协议/加密/登录）
- 生成分析报告

### 3. 更新ToDo.md
- 标记脱壳任务为进行中
- 添加子任务：复制产出、反编译DEX

---

## 三、你需要执行的操作

### 步骤1: 等待BlackDex完成
⏱️ 预计时间: 5-10分钟

**检查完成标志**:
- BlackDex显示"脱壳完成"
- `/sdcard/Download/BlackDex/com.minitech.miniworld/` 目录存在
- 有多个 `dump_*.dex` 文件

### 步骤2: 复制脱壳产出到电脑

**方法A: 使用ADB（推荐）**
```bash
# 在电脑上执行
adb pull /sdcard/Download/BlackDex/com.minitech.miniworld "https://github.com/StarsailsClover/MnMCPResources\packs_downloads\dumped_dex\"
```

**方法B: 使用文件管理器**
1. 在设备上使用文件管理器
2. 找到 `/sdcard/Download/BlackDex/com.minitech.miniworld/`
3. 压缩为ZIP
4. 发送到电脑
5. 解压到 `MnMCPResources/packs_downloads/dumped_dex/`

### 步骤3: 运行自动处理工具
```bash
cd tools/android_shell/
python process_dumped_dex.py
```

**这个工具会自动**:
1. 检查DEX文件
2. 反编译所有DEX
3. 分析关键类
4. 生成分析报告

---

## 四、同时推进的其他任务

### 🟡 任务1: PC端抓包准备
**状态**: ⬜ 待执行
**阻塞**: 无（可并行进行）

**操作步骤**:
```bash
# 1. 运行抓包准备工具
cd tools/pc_capture/
python pc_network_capture.py

# 2. 安装Proxifier（如果没有）
# 下载: https://www.proxifier.com/

# 3. 安装Wireshark（如果没有）
# 下载: https://www.wireshark.org/download.html
```

**产出**:
- Proxifier配置文件
- Wireshark过滤规则
- 抓包操作指南

### 🟡 任务2: 注册第二个测试账号
**状态**: ⬜ 待执行
**阻塞**: 无（可并行进行）

**操作步骤**:
1. 访问 https://www.mini1.cn/
2. 点击注册
3. 使用另一个手机号注册
4. 记录迷你号和密码
5. 更新 `setup/test_accounts.md`

### 🟡 任务3: 下载外服APK
**状态**: ⬜ 待执行
**阻塞**: 无（可并行进行）

**操作步骤**:
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

## 六、预期产出时间表

| 时间 | 任务 | 产出 |
|------|------|------|
| +10分钟 | BlackDex完成 | DEX文件（50-150MB） |
| +15分钟 | 复制到电脑 | `dumped_dex/` 目录 |
| +30分钟 | 自动处理 | 反编译源码 + 分析报告 |
| +1小时 | 初步分析 | 识别关键网络类 |
| +2小时 | PC抓包准备 | Proxifier配置 + Wireshark规则 |
| +1天 | 完整分析 | 协议结构初稿 |

---

## 七、常见问题预案

### Q: BlackDex脱壳失败？
**解决**:
1. 尝试 Youpk: https://github.com/Youlor/Youpk
2. 尝试 FDex2: https://github.com/ratchetrobotics/FDex2
3. 转向PC端抓包分析

### Q: DEX文件很小（< 10MB）？
**解决**:
- 脱壳不完整，尝试其他工具
- 或APK使用了SO库（C++层），需要分析SO文件

### Q: 反编译后代码混淆严重？
**解决**:
- 正常情况，使用字符串搜索
- 搜索关键词: "socket", "protocol", "AES", "login"
- 结合动态调试

---

## 八、检查点

### 检查点1: DEX文件复制完成
**标准**: `MnMCPResources/packs_downloads/dumped_dex/com.minitech.miniworld/` 存在且包含DEX文件
**验证**: 运行 `process_dumped_dex.py` 能检测到文件

### 检查点2: 自动处理完成
**标准**: 生成分析报告 `analysis/ANALYSIS_REPORT.md`
**验证**: 报告包含网络类、协议类、加密类列表

### 检查点3: 关键类识别
**标准**: 找到至少3个网络通信相关类
**验证**: 能定位到Socket连接、数据包发送代码

---

## 九、下一步会话计划

### Session 016: 脱壳结果分析
**触发条件**: BlackDex完成且DEX文件复制到电脑
**任务**:
1. 运行自动处理工具
2. 分析产出的关键类
3. 识别网络协议结构
4. 规划协议翻译层实现

### Session 017: PC端抓包执行
**触发条件**: Proxifier和Wireshark安装完成
**任务**:
1. 配置抓包环境
2. 执行抓包操作
3. 分析抓包数据
4. 对比PC和手游协议

---

## 十、总结

**当前状态**: 
- 🔴 主线: BlackDex脱壳进行中
- 🟡 支线: 准备并行推进其他任务

**关键路径**:
1. 等待脱壳完成 → 复制文件 → 自动处理 → 代码分析
2. （并行）安装抓包工具 → PC端抓包 → 协议对比

**风险**: 低
- BlackDex成功率较高
- 即使失败也有备选方案（PC抓包）

---

**下一步立即执行**:
1. ⏳ 等待BlackDex完成
2. 📋 复制DEX文件到电脑
3. 🚀 运行 `process_dumped_dex.py`

同时可以并行执行：
- 安装Proxifier和Wireshark
- 注册第二个测试账号
