# Before Development
务必主动维护该文档
<import src="BeforeDevelopment.md" />


## 1. MiniWorld_BlockID_Extraction_Package（方块ID提取工具包）
用途：从迷你世界游戏中提取方块ID映射表的技术工具包


文件|用途
|------|------|
block_id_hook.js|Frida Hook脚本，运行时拦截游戏进程获取方块ID
get_block_ids_runtime.py|Python脚本生成器，辅助生成Hook代码
capture_websocket.py|WebSocket抓包分析工具
block_mapping_complete.json|29个基础方块的推测映射表（待验证）
block_mapping_template.json|空白模板供填写
README_FOR_OPERATOR.md|操作员快速开始指南
BLOCK_ID_EXTRACTION_GUIDE.md|详细操作指南
提交结果模板.json|操作员填写结果的JSON模板
操作日志模板.md|操作过程记录模板

技术特点：

需要Root过的安卓设备
使用Frida框架进行动态分析
支持运行时Hook和网络抓包两种方法

## 2. Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay（核心项目仓库）
用途：完整的跨平台联机互通项目主仓库

目录结构：

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── docs/                          # 技术文档
│   ├── TechnicalDocument.md      # 技术架构文档
│   ├── ProjectPlan.md            # 项目规划与开发计划
│   ├── DevelopmentStatus.md      # 开发状态报告
│   ├── PROTOCOL_ANALYSIS_REPORT.md # 协议分析报告
│   ├── DEPLOYMENT_GUIDE.md       # 部署指南 ⭐ 新增
│   └── ...
├── src/                           # 源代码
│   ├── core/                      # 核心模块
│   │   ├── proxy_server.py       # 代理服务器
│   │   ├── protocol_translator.py # 协议翻译器
│   │   └── session_manager.py    # 会话管理器
│   └── protocol/                  # 协议处理
│       ├── block_mapper.py       # 方块映射
│       ├── miniworld_auth.py     # 迷你世界认证
│       ├── login_handler.py      # 登录处理
│       ├── coordinate_converter.py # 坐标转换
│       └── block_mapping_complete.json # 方块映射表
├── tools/                         # 工具集
│   ├── jadx/                     # APK反编译工具
│   ├── MiniWorld_BlockID_Extraction_Package/ # 方块ID提取包
│   ├── encrypt_config.py         # 配置加密工具 ⭐ 新增
│   ├── decrypt_config.py         # 配置解密工具 ⭐ 新增
│   └── package_resources.py      # 资源打包工具 ⭐ 新增
├── config/                        # 配置文件 ⭐ 新增
│   └── encrypted/                # 加密配置存储
│       └── config.json.template  # 配置模板
├── .github/                       # GitHub配置
│   ├── workflows/ci.yml          # CI/CD工作流
│   ├── PULL_REQUEST_TEMPLATE.md  # PR模板
│   ├── ISSUE_TEMPLATE/           # Issue模板
│   └── ...
├── deploy.py                      # 一键部署脚本 ⭐ 新增
├── README.md                      # 项目主文档
├── CHANGELOG.md                   # 更新日志
├── CONTRIBUTING.md                # 贡献指南
├── PROJECT_OVERVIEW.md            # 项目总览
├── BeforeDevelopment.md           # 本文件
└── COMPONENT_MANIFEST.json        # 组件清单
```

技术架构：

迷你四端 → 端适配层 → 协议翻译层 → Java中转服务端 → GeyserMC → MC全端

## 3. MnMCPResources（资源与备份仓库）
用途：项目资源文件、分析结果和历史备份

目录结构：
```
MnMCPResources/
├── Buckup/Step_1.8.1/       # 项目备份（版本1.8.1）
│   ├── docs/                # 架构文档
│   ├── src/core/            # 核心代码备份
│   └── tools/               # 工具脚本
├── Resources/               # 资源文件
│   ├── analysis/            # 分析结果
│   │   ├── dex_analysis/    # DEX字符串分析
│   │   └── pcap_analysis/   # 抓包分析
│   ├── apks/                # APK文件
│   ├── decompiled/          # 反编译结果
│   └── pc_versions/         # PC版本文件
├── packs_downloads/         # 下载的游戏包
│   └── dumped_dex/          # DEX脱壳文件
└── backupdocs/              # 会话备份文档
```

## 4. MnMCPWebsite（项目介绍网站） ⭐ 新增
用途：项目官方介绍网站

目录结构：
```
MnMCPWebsite/
├── index.html              # 主页面（响应式设计）
├── css/                   # 样式文件（待添加）
├── js/                    # JavaScript文件（待添加）
├── assets/                # 图片和资源（待添加）
└── README.md              # 网站文档
```

特性：
- 现代化响应式设计
- 渐变色主题
- 纯HTML/CSS，无需构建工具
- GitHub集成

## 开发手册
本手册用于规范项目全流程开发标准，保障开发质量、项目稳定性与后续可维护性

---

## 开发步骤执行状态

### ✅ 步骤1: 文档更新
- [x] 更新 README.md - 添加项目状态徽章和架构图
- [x] 创建 CHANGELOG.md - 记录版本变更
- [x] 创建 CONTRIBUTING.md - 贡献指南
- [x] 创建 DevelopmentStatus.md - 开发状态报告
- [x] 创建 DEPLOYMENT_GUIDE.md - 部署指南
- [x] 更新所有技术文档

### ✅ 步骤2: GitHub配置
- [x] 创建 PULL_REQUEST_TEMPLATE.md - PR模板
- [x] 创建 ISSUE_TEMPLATE/bug_report.md - Bug报告模板
- [x] 创建 ISSUE_TEMPLATE/feature_request.md - 功能请求模板
- [x] 更新 .github/workflows/ci.yml - CI/CD工作流

### ✅ 步骤3: 开发环境配置
- [x] 创建 requirements-dev.txt - 开发依赖
- [x] 确保 requirements.txt - 生产依赖完整
- [x] 配置 pre-commit hooks（可选）

### ✅ 步骤4: 代码整理
- [x] 更新 src/core/protocol_translator.py
- [x] 创建 src/protocol/miniworld_auth.py
- [x] 创建 src/protocol/coordinate_converter.py
- [x] 创建 src/protocol/block_mapping_complete.json
- [x] 整理 tools/ 目录结构

### ✅ 步骤5: 工具包准备
- [x] 创建 MiniWorld_BlockID_Extraction_Package/
- [x] 包含所有提取工具和文档
- [x] 准备提交模板和日志模板

### ✅ 步骤6: 部署和加密系统 ⭐ 新增
- [x] 创建 deploy.py - 一键部署脚本
- [x] 创建 DEPLOYMENT_GUIDE.md - 部署指南
- [x] 创建 tools/encrypt_config.py - 配置加密工具
- [x] 创建 tools/decrypt_config.py - 配置解密工具
- [x] 创建 config/encrypted/ - 加密配置目录
- [x] 创建 tools/package_resources.py - 资源打包工具

### ✅ 步骤7: 项目网站 ⭐ 新增
- [x] 创建 MnMCPWebsite/index.html - 介绍网站
- [x] 响应式设计，支持移动端
- [x] 渐变色主题
- [x] 纯HTML/CSS实现

### ⏳ 步骤8: GitHub推送准备
- [ ] 执行 git add .
- [ ] 执行 git commit -m "docs: 更新所有文档并整理项目结构"
- [ ] 执行 git push origin main
- [ ] 验证 CI/CD 工作流通过

---

## 推送前检查清单

### 文档完整性
- [x] README.md 已更新
- [x] CHANGELOG.md 已创建
- [x] CONTRIBUTING.md 已创建
- [x] DEPLOYMENT_GUIDE.md 已创建
- [x] LICENSE 文件存在
- [x] .gitignore 配置正确

### GitHub配置
- [x] .github/workflows/ci.yml 已更新
- [x] .github/PULL_REQUEST_TEMPLATE.md 已创建
- [x] .github/ISSUE_TEMPLATE/*.md 已创建

### 代码质量
- [x] 所有Python文件语法正确
- [x] 没有敏感信息泄露
- [x] 大文件已移至 MnMCPResources
- [x] COMPONENT_MANIFEST.json 已更新

### 部署系统
- [x] deploy.py 一键部署脚本
- [x] 加密/解密工具完整
- [x] 配置模板已创建
- [x] 资源打包工具

### 网站
- [x] MnMCPWebsite/index.html 已创建
- [x] 响应式设计
- [x] 链接正确

### 依赖管理
- [x] requirements.txt 完整
- [x] requirements-dev.txt 已创建
- [x] 没有不必要的依赖

---

## 敏感信息加密说明

### 加密机制
- **算法**: Fernet (基于AES-256-CBC)
- **密钥派生**: PBKDF2HMAC (SHA256, 480000 iterations)
- **盐值**: 随机16字节，存储在加密文件中

### 使用流程
1. **开发阶段**: 编辑 `config/config.json`
2. **加密**: `python tools/encrypt_config.py encrypt`
3. **提交**: 只提交加密后的文件到GitHub
4. **部署**: 运行 `deploy.py`，输入密码自动解密

### 文件位置
- 加密文件: `config/encrypted/*.enc`
- 解密工具: `tools/decrypt_config.py`
- 模板: `config/encrypted/config.json.template`

---

## Git推送命令

```bash
# 1. 检查状态
git status

# 2. 添加所有更改
git add .

# 3. 提交更改
git commit -m "docs: 更新所有文档并整理项目结构

- 更新 README.md，添加项目状态徽章和架构图
- 创建 CHANGELOG.md 记录版本变更
- 创建 CONTRIBUTING.md 贡献指南
- 创建 DevelopmentStatus.md 开发状态报告
- 创建 DEPLOYMENT_GUIDE.md 部署指南
- 更新 GitHub 配置（PR模板、Issue模板）
- 更新 CI/CD 工作流至最新版本
- 创建方块ID提取工具包
- 添加坐标转换器和认证模块
- 创建一键部署脚本 deploy.py
- 添加配置加密/解密工具
- 创建资源打包工具
- 创建项目介绍网站 MnMCPWebsite
- 整理项目目录结构"

# 4. 推送到GitHub
git push origin main

# 5. 验证CI/CD
gitHub Actions 应该自动运行并显示绿色勾选
```

---

## 部署后验证

### 1. 网站验证
- [ ] 访问 GitHub Pages 或自有服务器
- [ ] 确认网站正常显示
- [ ] 检查响应式设计

### 2. 部署脚本验证
- [ ] 运行 `python deploy.py --mode=minimal`
- [ ] 确认解密功能正常
- [ ] 检查目录结构

### 3. CI/CD验证
- [ ] 检查 Actions 状态
- [ ] 确认所有检查通过

---

**最后更新**: 2026-02-26  
**状态**: 准备推送GitHub