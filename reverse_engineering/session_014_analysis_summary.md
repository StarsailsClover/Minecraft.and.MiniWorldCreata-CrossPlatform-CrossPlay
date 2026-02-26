# 逆向工程会话记录 - Session 014
## 任务: 项目断点分析与下一步规划
## 日期: 2026-02-26
## 状态: 完成

---

## 一、项目现状全面审查

### 1.1 文档审查结果

已审查文档:
- ✅ README.md - 项目概述和技术架构
- ✅ PROJECT_OVERVIEW.md - 项目结构和核心模块
- ✅ ToDo.md - 开发任务清单（已更新）
- ✅ TechnicalDocument.md - 技术架构详细设计
- ✅ ProjectPlan.md - 项目规划和风险分析
- ✅ COMPONENT_MANIFEST.json - 组件清单
- ✅ session_001~013 - 历史会话记录

### 1.2 代码实现审查

已审查代码:
- ✅ path_resolver.py - 路径解析工具
- ✅ check_and_fix_components.py - 组件检查脚本
- ✅ decompile_checkpoint.py - 断点续传反编译
- ✅ packet_analyzer.py - 数据包分析器框架
- ✅ download_apk.py - APK下载脚本

### 1.3 资源目录审查

主文件夹 (`Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay`):
- ✅ 工具组件 (tools/) - 完整
- ✅ 服务端组件 (server/) - PaperMC + GeyserMC 配置完成
- ✅ 协议分析框架 (protocol_analysis/) - 基础框架
- ✅ 文档 (docs/) - 完整

资源文件夹 (`MnMCPResources`):
- ✅ 官服APK (miniworldMini-wp.apk, 1.60 GB) - 已反编译
- ✅ PC版目录结构 - 已提取
- ✅ 反编译输出 (decompiled_official/, decompiled/pc/) - 已完成

---

## 二、关键发现

### 🔴 重大发现: APK加固

**问题**: 官服APK反编译后只有5个smali文件

**分析**:
```bash
# 反编译结果检查
包名: com.minitech.miniworld（确认是官服）
smali文件数: 5个（异常，正常应有数千个）
关键类:
  - com.ace.gshell.AceApplication（腾讯御安全入口）
  - com.ace.gshell.mainFunction
  - com.ace.gshell.a/b/c（壳相关类）
```

**结论**: 
- APK使用了**腾讯御安全（Ace GShell）**加固保护
- 真实DEX文件在运行时才解密加载
- **必须进行脱壳才能获取协议代码**

### 🟡 PC端状态

**已完成**:
- ✅ 目录结构提取（miniworldPC_CN/）
- ✅ 关键文件识别（iworldpc.exe, MicroMiniNew.exe等）
- ✅ 日志文件分析（GameApp.log）

**待完成**:
- ⬜ 网络抓包分析
- ⬜ 协议逆向

### 🟢 测试账号

**已确认**:
- 账号A: 迷你号 2056574316，密码 ebjz985211
- 平台: PC + Android互通 ✅

**待准备**:
- 账号B: 需要注册第二个账号用于联机测试

---

## 三、断点识别

### 关键断点（阻塞后续开发）

| 优先级 | 断点 | 影响 | 解决方案 |
|--------|------|------|----------|
| 🔴 P0 | APK脱壳 | 无法获取协议代码 | 使用Frida/Youpk/BlackDex脱壳 |
| 🔴 P0 | PC端抓包 | 无法分析PC协议 | 使用Proxifier + Wireshark |
| 🟡 P1 | 第二账号 | 无法测试联机 | 注册新账号 |
| 🟡 P1 | 外服APK | 无法对比协议 | 从APKPure下载 |
| 🟢 P2 | Wireshark环境 | 影响抓包效率 | 安装配置 |

### 已完成任务（无需继续）

- ✅ 基础架构搭建
- ✅ 开发环境配置
- ✅ 大文件管理
- ✅ 组件完整性检查
- ✅ 官服APK下载和初步反编译
- ✅ PC端目录结构提取

---

## 四、已执行操作

### 4.1 更新ToDo.md
- 重新组织任务结构，区分手游端/PC端/外服
- 添加脱壳任务
- 添加PC端抓包任务
- 添加下一步行动计划

### 4.2 创建新工具

#### 工具1: Android脱壳工具
```
tools/android_shell/frida_dump.py
- 使用Frida进行动态脱壳
- 针对腾讯御安全加固
- 生成Frida脚本和配置
```

#### 工具2: PC端抓包工具
```
tools/pc_capture/pc_network_capture.py
- 分析游戏日志文件
- 生成Proxifier配置
- 创建Wireshark过滤规则
- 输出抓包指南
```

### 4.3 创建详细计划文档
```
docs/NextSteps.md
- 当前状态总结
- 下一步行动（按优先级排序）
- 推荐执行顺序
- 技术难点与解决方案
- 检查点和风险分析
```

---

## 五、下一步行动（立即执行）

### 选项1: Android端脱壳（推荐优先尝试）

**目标**: 获取真实DEX文件

**步骤**:
1. 准备Root过的Android设备或模拟器
2. 安装Frida Server
3. 运行脱壳脚本:
   ```bash
   cd tools/android_shell/
   python frida_dump.py
   ```
4. 验证脱壳结果（DEX文件应 > 50MB）

**预期时间**: 1-2天
**成功率**: 70%（取决于设备环境和加固版本）

### 选项2: PC端网络抓包（可并行）

**目标**: 通过抓包分析协议

**步骤**:
1. 安装Proxifier和Wireshark
2. 运行抓包准备脚本:
   ```bash
   cd tools/pc_capture/
   python pc_network_capture.py
   ```
3. 配置Proxifier规则
4. 启动Wireshark抓包
5. 运行游戏并执行操作
6. 分析抓包数据

**预期时间**: 1天
**成功率**: 90%（抓包技术成熟）

### 建议执行策略

**并行执行**:
- 主线: Android脱壳（优先级高，获取完整代码）
- 支线: PC端抓包（优先级中，验证协议可行性）

**原因**:
1. Android脱壳如果成功，可以获取完整的协议实现
2. PC端抓包相对简单，可以快速验证协议分析可行性
3. 两者可以相互验证（对比PC和手游协议差异）

---

## 六、风险提醒

### 技术风险
1. **脱壳失败**: 腾讯御安全可能有反调试/反脱壳机制
   - 应对: 尝试多种脱壳工具，或转向纯抓包分析

2. **强加密协议**: 即使脱壳成功，协议可能使用强加密
   - 应对: 动态调试获取密钥，或分析密钥交换流程

3. **反作弊检测**: ACE系统可能检测异常行为
   - 应对: 使用备用设备/模拟器，避免主力设备

### 项目风险
1. **时间延误**: 脱壳可能比预期耗时
   - 应对: 设定时间上限（3天），超时转向其他方案

2. **协议复杂度**: 迷你世界协议可能比预期复杂
   - 应对: 分阶段实现，先做基础功能（移动/聊天）

---

## 七、检查点设定

### 检查点1: 脱壳成功（3天内）
**标准**: 获取到 > 50MB 的DEX文件
**验证**: 使用jadx反编译，能看到游戏逻辑代码

### 检查点2: 协议识别（1周内）
**标准**: 识别出登录、房间、同步三个核心协议
**验证**: 能解析出数据包结构

### 检查点3: 原型实现（2周内）
**标准**: 实现基础代理功能（连接转发）
**验证**: 能建立连接并转发数据

---

## 八、总结

### 当前项目健康度: 🟡 中等

**优势**:
- 基础架构完整
- 工具链齐全
- 文档完善
- 测试账号已确认

**劣势**:
- 核心协议获取受阻（APK加固）
- 需要额外的脱壳/抓包工作
- 技术难度高于预期

### 关键决策

**决策**: 采用"双轨并行"策略
1. **轨道A**: Android脱壳（主攻方向）
2. **轨道B**: PC端抓包（辅助验证）

**理由**: 脱壳可以获取完整代码，但风险较高；抓包相对简单，但信息可能不完整。两者结合可以提高成功率。

---

## 九、立即执行清单

- [ ] 准备Android设备（Root）或安装模拟器
- [ ] 安装Proxifier和Wireshark
- [ ] 运行 `tools/android_shell/frida_dump.py`
- [ ] 运行 `tools/pc_capture/pc_network_capture.py`
- [ ] 注册第二个迷你世界测试账号
- [ ] 开始脱壳或抓包操作

---

**下一步会话**: Session 015 - Android脱壳或PC抓包执行
