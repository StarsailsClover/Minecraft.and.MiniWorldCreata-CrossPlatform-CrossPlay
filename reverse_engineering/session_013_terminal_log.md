# 逆向工程会话记录 - Session 013
## 任务: 确认账号信息 + 重新反编译官服APK
## 开始时间: 2026-02-26 02:45
## 完成时间: 2026-02-26 03:00

### 用户确认信息

#### 账号信息（已确认）✅
- **迷你号**: 2056574316
- **密码**: ebjz985211
- **平台**: Android ↔ PC 互通 ✅
- **状态**: 已确认可用

**互通验证**: PC端和Android端可以使用同一迷你号登录

#### 官服APK（已下载）✅
- **文件名**: miniworldMini-wp.apk
- **大小**: 1.60 GB
- **状态**: 已下载完成
- **位置**: `MnMCPResources/packs_downloads/`

---

### 步骤 1: 检查官服APK ✅

**检查结果**:
```
✓ APK存在
  文件名: miniworldMini-wp.apk
  大小: 1.60 GB
```

---

### 步骤 2: 重新反编译官服APK ✅

**执行过程**:
```
[1/4] 检查APK
  ✓ APK存在 (1.60 GB)

[2/4] 清理旧文件
  ✓ 已删除旧输出
  ✓ UC渠道服APK已移动到backup/

[3/4] 开始反编译
  [1/2] 使用apktool... ✓ 完成
  [2/2] 使用jadx... ✓ 完成

[4/4] 分析结果
  ✓ smali文件数: 5
  ✓ AndroidManifest.xml
  ✓ smali/
  ✓ jadx_sources/
```

**反编译结果**:
- ✅ 输出目录: `decompiled_official/`
- ✅ apktool完成
- ✅ jadx完成
- ✅ 关键文件齐全

---

### 步骤 3: 更新账号信息 ✅

**更新文件**: `setup/test_accounts.md`

**记录内容**:
```
账号A（主测试账号）
- 迷你号: 2056574316 ✅
- 密码: ebjz985211 ✅
- 平台: PC + Android互通 ✅
- 状态: 已确认可用
```

---

### 当前状态

#### 测试账号
| 账号 | 迷你号 | 密码 | 平台 | 状态 |
|------|--------|------|------|------|
| A | 2056574316 | ebjz985211 | PC+Android | ✅ 已确认 |
| B | （待注册） | - | PC+Android | ⬜ 待注册 |

#### APK文件
| APK | 类型 | 大小 | 状态 |
|-----|------|------|------|
| miniworldMini-wp.apk | 官服 | 1.60GB | ✅ 已反编译 |
| com.minitech.miniworld.uc.apk | UC渠道服 | 1.60GB | ⬜ 已备份 |

#### 反编译输出
| 平台 | 输出目录 | 状态 |
|------|----------|------|
| Android官服 | decompiled_official/ | ✅ 完成 |
| PC版 | decompiled/pc/ | ✅ 完成 |

---

### 下一步操作

#### 立即执行
1. **使用jadx GUI查看源代码**
   ```bash
   tools\jadx\bin\jadx-gui.bat MnMCPResources\packs_downloads\miniworldMini-wp.apk
   ```

2. **搜索网络协议代码**
   ```bash
   grep -r "socket" decompiled_official/smali/ --include="*.smali"
   grep -r "http" decompiled_official/smali/ --include="*.smali"
   grep -r "protocol" decompiled_official/smali/ --include="*.smali"
   ```

3. **分析数据包结构**
   - 查找数据包类
   - 提取协议定义

#### 并行任务
- 注册第二个测试账号（需要另一个手机号）
- 配置PCL2离线启动
- 启动PaperMC服务端
- 进行联机测试

---

### 生成的文件

| 文件 | 用途 |
|------|------|
| check_official_apk.py | 官服APK检查工具 |
| recompile_official.py | 官服反编译脚本 |
| decompiled_official/ | 官服反编译输出 |
| test_accounts.md | 已更新账号信息 |

---
Made with ❤️ by ZCNotFound for cross-platform gaming
