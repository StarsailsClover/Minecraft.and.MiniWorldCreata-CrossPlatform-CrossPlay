# 逆向工程会话记录 - Session 005
## 任务: 全面检查组件完整性、修复硬编码路径、创建组件清单
## 开始时间: 2026-02-26 00:45
## 完成时间: 2026-02-26 01:00

### 步骤 1: 运行组件完整性检查

创建了 `check_and_fix_components.py` 脚本进行全面检查。

检查结果:
```
[检查] tools
  ✓ apktool.jar (APK反编译工具)
  ✓ apktool.bat (APK工具脚本)
  ✓ jadx/ (Java反编译器)
  ✓ frida-server.xz (Frida服务端)

[检查] server/paper
  ✓ paper-1.20.6-151.jar (PaperMC服务端)
  ✓ paper.jar (PaperMC软链接)
  ✓ eula.txt (EULA协议)
  ✓ server.properties (服务器配置)

[检查] server/plugins
  ✓ Geyser-Spigot.jar (GeyserMC插件)
  ✓ floodgate-spigot.jar (Floodgate插件)

[检查] server/fabric
  ✓ fabric-installer.jar (Fabric安装器)

[检查] server/mods
  ✓ fabric-api-0.98.0.jar (Fabric API)
```

### 步骤 2: 检查大文件位置

结果: ✓ 项目目录中没有超过100MB的文件

所有大文件已正确移动到外部目录:
- miniworld_cn_1.53.1.apk (1.60 GB) → MnMCPResources/apk_downloads/

### 步骤 3: 检查外部资源引用

结果: ✓ APK位置文件正确指向外部目录

位置文件内容:
```
FILE_MOVED_TO:
https://github.com/StarsailsClover/MnMCPResources\apk_downloads\miniworld_cn_1.53.1.apk
```

### 步骤 4: 发现并修复硬编码路径问题

**发现的问题:**
1. `apk_downloads/decompile_miniworld_cn.py` 包含硬编码路径
2. `apk_downloads/decompile_apk.py` 包含硬编码路径

**修复方案:**
将硬编码路径改为动态计算:
```python
# 动态获取路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXTERNAL_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "MnMCPResources")

# 动态解析APK路径
def get_apk_path():
    # 1. 检查外部目录
    # 2. 检查项目目录
    # 3. 检查.location文件
    # 4. 返回找到的路径
```

### 步骤 5: 创建路径解析工具

创建了 `path_resolver.py` 统一处理所有路径:
- `resolve_path(rel_path)` - 通用路径解析
- `get_apk_path(apk_name)` - 获取APK路径
- `get_tool_path(tool_name)` - 获取工具路径
- `get_server_path(server_file)` - 获取服务端路径

### 步骤 6: 创建组件清单文件

创建了 `COMPONENT_MANIFEST.json` 完整记录:
- 所有组件的位置和状态
- 文件大小和描述
- Git忽略规则
- 新成员设置指南

### 步骤 7: 创建.gitignore

创建了 `.gitignore` 文件:
```
MnMCPResources/    # 外部资源目录
*.apk              # APK文件
*_decompiled/      # 反编译输出
*.log              # 日志文件
__pycache__/       # Python缓存
...
```

### 修复的文件清单

| 文件 | 修复内容 |
|------|----------|
| decompile_miniworld_cn.py | 移除硬编码路径，使用动态路径计算 |
| decompile_apk.py | 移除硬编码路径，使用动态路径计算 |
| path_resolver.py | 创建统一路径解析工具 |
| COMPONENT_MANIFEST.json | 创建完整组件清单 |
| .gitignore | 创建Git忽略规则 |

### 当前组件状态

#### 项目目录（GitHub提交）
```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── tools/                    # <100MB ✓
├── server/                   # <100MB ✓
├── apk_downloads/            # 脚本和文档 ✓
├── docs/                     # 文档 ✓
├── reverse_engineering/      # 记录 ✓
├── path_resolver.py          # 路径工具 ✓
├── check_and_fix_components.py # 检查工具 ✓
├── COMPONENT_MANIFEST.json   # 组件清单 ✓
├── .gitignore               # Git忽略 ✓
└── ...其他小文件
```

#### 外部目录（大文件存储）
```
MnMCPResources/
└── apk_downloads/
    └── miniworld_cn_1.53.1.apk    # 1.60 GB ✓
```

### 路径解析示例

```python
# 使用path_resolver获取路径
import path_resolver

# 获取APK路径（自动处理外部目录）
apk_path = path_resolver.get_apk_path("miniworld_cn_1.53.1.apk")
# 返回: https://github.com/StarsailsClover/MnMCPResources\apk_downloads\miniworld_cn_1.53.1.apk

# 获取工具路径
tool_path = path_resolver.get_tool_path("apktool.jar")
# 返回: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\apktool.jar

# 获取服务端路径
server_path = path_resolver.get_server_path("paper/paper.jar")
# 返回: https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\server\paper\paper.jar
```

### GitHub提交优势

1. **无大文件警告**: 所有>100MB文件在外部目录
2. **简明仓库**: 只包含代码和文档
3. **快速克隆**: 无需下载大文件
4. **路径兼容**: 新成员可自定义外部目录位置

### 新成员设置流程

```bash
# 1. 克隆仓库
git clone <repo-url>

# 2. 创建外部目录
mkdir C:\Users\<用户名>\Documents\Coding\MnMCPResources

# 3. 下载APK（参考MANUAL_DOWNLOAD_GUIDE.md）
# 保存到外部目录/apk_downloads/

# 4. 验证路径
python path_resolver.py

# 5. 检查完整性
python check_and_fix_components.py
```

### 断点记录
- 当前步骤: 组件完整性检查和修复完成
- 状态: ✓ 所有组件正常，路径问题已修复
- 反编译状态: 仍在后台运行
- 下一步: 等待反编译完成，开始协议分析

---
Made with ❤️ by ZCNotFound for cross-platform gaming
