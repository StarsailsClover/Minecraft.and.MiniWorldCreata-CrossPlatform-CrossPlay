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

技术特点：

需要Root过的安卓设备
使用Frida框架进行动态分析
支持运行时Hook和网络抓包两种方法

## 2. Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay（核心项目仓库）
用途：完整的跨平台联机互通项目主仓库

目录结构：

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── docs/                    # 技术文档
│   ├── TechnicalDocument.md # 技术架构文档
│   ├── ProjectPlan.md       # 项目规划与开发计划
│   └── ...
├── src/                     # 源代码
│   ├── core/                # 核心模块
│   │   ├── proxy_server.py      # 代理服务器
│   │   ├── protocol_translator.py # 协议翻译器
│   │   └── session_manager.py   # 会话管理器
│   └── protocol/            # 协议处理
│       ├── block_mapper.py      # 方块映射
│       ├── miniworld_auth.py    # 迷你世界认证
│       ├── login_handler.py     # 登录处理
│       └── coordinate_converter.py # 坐标转换
└── tools/                   # 工具集
    └── jadx/                # APK反编译工具
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
└── backupdocs/              # 会话备份文档
```

## 开发手册
本手册用于规范项目全流程开发标准，保障开发质量、项目稳定性与后续可维护性。

### 1. 准备工作
1. 基础环境安装
   确保本地/服务器已完成 **Java、Python、Node.js** 等核心开发环境安装，优先使用稳定版，避免版本兼容问题。
2. 环境校验
   执行版本检查、依赖加载测试，确认所有开发环境正常运行、无缺失组件。
3. 工具配置
   完成IDE、版本控制工具（Git）、包管理工具等开发配套工具的配置与调试。

### 2. 构建项目
1. 前置环境核查
   开发启动前，全面检查已配置环境、依赖包、历史开发组件及关联模块，排除冲突风险。
2. 风险防控
   严格执行前置检查，杜绝因局部异常引发**雪崩式连锁反应**，防止影响整体项目开发与运行。
3. 项目初始化
   按团队规范搭建项目目录结构、基础配置文件，完成项目骨架初始化。

### 3. 开发步骤
严格按照以下标准化流程执行，确保开发闭环、文档完整、可直接交付：
1. 检查：全面核查项目状态、依赖、配置及历史开发内容，确认开发条件就绪
2. 开发：依据需求与设计规范，完成功能模块代码编写
3. 测试：开展单元测试、本地自测，修复基础逻辑与功能bug
4. 部署：将开发内容推送至测试环境，完成环境部署
5. 验证：在测试环境进行功能、联调、兼容性全维度验证
6. 全文档验证更新：核对并更新现有技术文档，保证与开发内容一致
7. 创建新的相关文档：为新增功能编写接口文档、使用说明、开发注释等配套文档
8. 创建自动化部署脚本：编写可复用、供他人直接使用的自动化部署脚本
9. Releases创建：按规范生成项目正式版本，标注更新日志与版本信息
10. 备份及其文档创建：完成项目代码/配置备份，并编写备份说明与恢复文档
11. 清除无须上传的文件：清理临时文件、测试文件、冗余日志等无效文件
12. 开发脚本归档：将第一手开发用脚本统一移至 `/MnMCPDevelopment/Scripts` 目录
13. 引用与组件验证：校验文件引用路径、组件调用逻辑，确保组件完整、引用无误