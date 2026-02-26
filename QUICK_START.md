# 快速开始指南

5分钟内完成项目设置并开始使用

---

## 目录

1. [新成员设置](#新成员设置)
2. [日常使用](#日常使用)
3. [故障排除](#故障排除)

---

## 新成员设置

### 步骤1: 克隆仓库 (1分钟)

```bash
# 克隆GitHub仓库
git clone https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git

# 进入项目目录
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
```

### 步骤2: 创建外部目录 (1分钟)

```powershell
# 创建外部资源目录（用于存储大文件）
mkdir "C:\Users\$env:USERNAME\Documents\Coding\MnMCPResources\apk_downloads"
```

### 步骤3: 下载APK文件 (2分钟)

**迷你世界国服 1.53.1**:
1. 访问 https://www.mini1.cn/
2. 点击"安卓下载"
3. 保存到: `MnMCPResources/apk_downloads/miniworld_cn_1.53.1.apk`

**其他APK**（可选）:
- MiniWorld: Creata 1.7.15 - https://apkpure.net/mini-world-creata
- Minecraft Bedrock - 需Google Play购买

### 步骤4: 验证设置 (1分钟)

```bash
# 验证路径解析
python path_resolver.py

# 检查组件完整性
python check_and_fix_components.py
```

✅ 设置完成！

---

## 日常使用

### 启动APK反编译

```bash
cd apk_downloads

# 启动反编译（后台运行）
python decompile_checkpoint.py

# 查看状态
python decompile_checkpoint.py status

# 查看日志
type ..\reverse_engineering\decompile_log.txt
```

### 生成协议报告

```bash
python protocol_analysis\packet_analyzer.py
```

### 启动Minecraft服务端

```bash
cd server
start.bat
```

### 使用jadx查看源代码

```bash
# 启动jadx GUI
.\tools\jadx\bin\jadx-gui.bat C:\Users\%USERNAME%\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_1.53.1.apk
```

---

## 故障排除

### 问题1: "APK文件不存在"

**原因**: APK未下载或路径错误

**解决**:
```bash
# 检查APK位置
ls C:\Users\%USERNAME%\Documents\Coding\MnMCPResources\apk_downloads\

# 确认文件名
# 应为: miniworld_cn_1.53.1.apk
```

### 问题2: "工具未找到"

**原因**: 工具未下载或路径错误

**解决**:
```bash
# 运行完整性检查
python check_and_fix_components.py

# 工具应位于:
# - tools/apktool.jar
# - tools/jadx/
```

### 问题3: 反编译失败

**原因**: 内存不足或APK损坏

**解决**:
```bash
# 重置检查点
python decompile_checkpoint.py reset

# 重新启动
python decompile_checkpoint.py

# 检查日志
type reverse_engineering\decompile_log.txt
```

### 问题4: 路径解析错误

**原因**: 外部目录位置不正确

**解决**:
```python
# 编辑 path_resolver.py 修改 EXTERNAL_DIR
EXTERNAL_DIR = r"C:\Users\你的用户名\Documents\Coding\MnMCPResources"
```

---

## 常用命令速查

| 命令 | 用途 |
|------|------|
| `python decompile_checkpoint.py` | 启动反编译 |
| `python decompile_checkpoint.py status` | 查看状态 |
| `python decompile_checkpoint.py reset` | 重置检查点 |
| `python check_and_fix_components.py` | 检查完整性 |
| `python path_resolver.py` | 测试路径解析 |
| `python protocol_analysis\packet_analyzer.py` | 生成协议报告 |
| `server\start.bat` | 启动MC服务端 |

---

## 获取帮助

- 查看 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) 了解项目结构
- 查看 [docs/TechnicalDocument.md](docs/TechnicalDocument.md) 了解技术细节
- 查看会话记录 `reverse_engineering/session_*.md`

---

Made with ❤️ by ZCNotFound for cross-platform gaming
