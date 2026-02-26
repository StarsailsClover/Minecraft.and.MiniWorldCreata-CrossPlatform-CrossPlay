# GitHub项目结构

**版本**: 1.0.0  
**日期**: 2026-02-26

---

## 📁 项目结构

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── .github/                    # GitHub配置
│   └── workflows/              # CI/CD工作流
├── src/                        # 核心源代码
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── proxy_server.py     # 代理服务器
│   │   ├── protocol_translator.py  # 协议翻译器
│   │   └── session_manager.py  # 会话管理器
│   └── protocol/               # 协议处理
│       ├── __init__.py
│       ├── login_handler.py    # 登录处理
│       ├── coordinate_converter.py  # 坐标转换
│       └── block_mapper.py     # 方块映射
├── tests/                      # 测试代码
│   ├── test_protocol.py        # 单元测试
│   ├── test_integration.py     # 集成测试
│   └── test_performance.py     # 性能测试
├── tools/                      # 工具脚本
│   ├── debug/                  # 调试工具
│   │   └── packet_inspector.py
│   ├── pc_capture/             # PC抓包工具
│   └── android_shell/          # Android工具
├── docs/                       # 文档
│   ├── ProtocolAnalysisReport.md   # 协议分析报告
│   ├── ProtocolImplementation.md   # 协议实现文档
│   ├── Phase1_Architecture.md      # 架构设计
│   └── TechnicalDocument.md        # 技术文档
├── config/                     # 配置文件
│   └── config.example.json     # 示例配置
├── scripts/                    # 脚本
│   ├── setup.ps1               # Windows安装脚本
│   ├── setup.sh                # Linux/Mac安装脚本
│   └── create_release.py       # 发布脚本
├── releases/                   # 发布包（gitignore）
│   └── mnmcp-v1.0.0.zip        # Release包
├── README.md                   # 项目介绍
├── DEPLOYMENT_GUIDE.md         # 部署指南
├── PROJECT_COMPLETE.md         # 完成报告
├── LICENSE                     # 许可证
├── requirements.txt            # 依赖列表
├── .gitignore                  # Git忽略规则
├── start_proxy.py              # 启动脚本
└── test_import.py              # 导入测试
```

---

## 📦 文件分类

### 核心代码 (GitHub)
| 目录 | 大小 | 说明 |
|------|------|------|
| src/ | ~43 KB | 核心源代码 |
| tests/ | ~15 KB | 测试代码 |
| tools/ | ~50 KB | 工具脚本 |
| docs/ | ~100 KB | 文档 |
| **总计** | **~208 KB** | **纯代码** |

### 外部资源 (不上传)
| 目录 | 大小 | 说明 |
|------|------|------|
| Resources/apks/ | 2.6 GB | APK文件 |
| Resources/analysis/ | 100 MB | 分析结果 |
| Resources/captures/ | 50 MB | 抓包数据 |
| Buckup/ | 50 MB | 版本备份 |

---

## 🚀 快速部署

### 方式1: Git Clone

```bash
# 1. 克隆仓库
git clone https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git
cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay

# 2. 运行安装脚本
# Windows:
.\scripts\setup.ps1
# Linux/Mac:
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. 启动代理
python start_proxy.py
```

### 方式2: Release包

```bash
# 1. 下载Release包
wget https://github.com/StarsailsClover/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/releases/download/v1.0.0/mnmcp-v1.0.0.zip

# 2. 解压
unzip mnmcp-v1.0.0.zip
cd mnmcp-v1.0.0

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动代理
python start_proxy.py
```

---

## ✅ 部署检查清单

### 环境检查
- [ ] Python 3.11+
- [ ] pip 可用
- [ ] 网络连接正常

### 安装检查
- [ ] 虚拟环境创建成功
- [ ] 依赖安装成功
- [ ] 配置文件创建成功

### 运行检查
- [ ] 代理服务器启动成功
- [ ] 端口25565监听正常
- [ ] Minecraft可以连接

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| Python文件 | 20+ |
| 代码行数 | ~4,000 |
| 测试用例 | 12 |
| 文档页数 | 33+ |
| 抓包数据 | 67,197个 |
| DEX文件 | 81个 |

---

## 🔧 维护脚本

| 脚本 | 用途 |
|------|------|
| `scripts/setup.ps1` | Windows安装 |
| `scripts/setup.sh` | Linux/Mac安装 |
| `scripts/create_release.py` | 创建Release包 |
| `test_import.py` | 验证导入 |
| `start_proxy.py` | 启动代理 |

---

## 📄 关键文档

| 文档 | 说明 |
|------|------|
| README.md | 项目介绍 |
| DEPLOYMENT_GUIDE.md | 详细部署指南 |
| ProtocolAnalysisReport.md | 协议分析报告 |
| PROJECT_COMPLETE.md | 项目完成报告 |

---

**项目已准备好上传GitHub！** ✅
