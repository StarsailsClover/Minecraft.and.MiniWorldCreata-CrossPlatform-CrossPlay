# ACE反作弊脱壳方案

**文档类型**: 技术研究  
**目标**: 迷你世界国服PC版DLL脱壳  
**状态**: 🔬 研究阶段

---

## ⚠️ 法律声明

本文档仅供安全研究和学习交流使用。未经授权的反编译、脱壳行为可能：
1. 违反软件许可协议
2. 触犯计算机犯罪相关法律
3. 导致账号永久封禁

**请在合法授权范围内使用本文档内容。**

---

## 🔍 ACE保护机制分析

### 1. 代码保护
- **代码段加密**: 关键代码段在运行时才解密
- **内存保护**: 使用VirtualProtect防止内存读取
- **完整性校验**: 运行时校验代码完整性

### 2. 反调试机制
- **调试器检测**: IsDebuggerPresent, CheckRemoteDebuggerPresent
- **硬件断点检测**: Dr0-Dr7寄存器检查
- **时序检测**: 检测单步执行的时间异常

### 3. 反Dump机制
- **内存混淆**: 关键数据动态解密
- **代码虚拟化**: 部分代码使用VM保护
- **完整性校验**: 定期校验内存完整性

---

## 🛠️ 脱壳方案

### 方案1: 内存Dump（推荐）

#### 原理
在代码解密后、执行前，从内存中Dump出解密后的代码。

#### 工具
- **x64dbg**: 动态调试器
- **Scylla**: PE重建工具
- **Cheat Engine**: 内存搜索

#### 步骤
```
1. 启动迷你世界，等待完全加载
2. 附加x64dbg到游戏进程
3. 找到代码解密后的内存区域
4. 设置断点在关键函数入口
5. Dump内存区域
6. 使用Scylla重建PE文件
```

#### 关键断点
```cpp
// 在以下API设置断点
VirtualProtect
VirtualProtectEx
NtProtectVirtualMemory
// 当权限从RX变为RW时，代码可能已解密
```

### 方案2: 钩子绕过

#### 原理
Hook ACE的校验函数，使其总是返回成功。

#### 代码示例
```cpp
// 绕过完整性校验
BOOL WINAPI Hooked_VerifyIntegrity() {
    return TRUE; // 总是返回成功
}

// 安装钩子
void InstallHook() {
    // 使用MinHook或Detours
    MH_Initialize();
    MH_CreateHook(
        (LPVOID)VerifyIntegrityAddr,
        (LPVOID)Hooked_VerifyIntegrity,
        (LPVOID*)&Original_VerifyIntegrity
    );
    MH_EnableHook((LPVOID)VerifyIntegrityAddr);
}
```

### 方案3: 驱动级Dump

#### 原理
使用内核驱动绕过用户层保护。

#### 工具
- **WinDbg**: 内核调试器
- **KDMapper**: 驱动加载器
- **自定义驱动**: 内存读取

#### 风险
- 可能触发反作弊
- 需要禁用驱动签名强制
- 系统稳定性风险

---

## 📋 具体操作流程

### 准备工作

1. **环境准备**
   ```
   - Windows 10/11
   - x64dbg (带Scylla插件)
   - Process Hacker 2
   - PE-bear (PE分析)
   ```

2. **关闭保护**
   ```
   - 关闭Windows Defender实时保护
   - 关闭其他安全软件
   - 确保有系统还原点
   ```

### 内存Dump步骤

#### Step 1: 定位目标DLL
```
1. 启动迷你世界
2. 打开Process Hacker 2
3. 找到游戏进程
4. 查看加载的DLL列表
5. 重点关注:
   - libSandboxGame.dll (53MB)
   - libSandBoxEngine.dll (27MB)
   - libiworld.dll (25MB)
```

#### Step 2: 分析内存布局
```
1. 在Process Hacker中右键DLL
2. 选择"Properties"
3. 查看Memory标签
4. 记录各段的内存地址和权限
5. 关注RX权限的代码段
```

#### Step 3: 设置断点
```
1. 附加x64dbg到游戏进程
2. Ctrl+G跳转到DLL基址
3. 在代码段入口设置断点
4. 运行游戏触发断点
5. 检查内存是否已解密
```

#### Step 4: Dump内存
```
1. 在x64dbg中，右键内存窗口
2. 选择"Follow in Memory Map"
3. 找到代码段
4. 右键 -> "Dump Memory to File"
5. 保存为.raw文件
```

#### Step 5: 重建PE
```
1. 打开Scylla
2. 选择正确的进程
3. 设置OEP (原始入口点)
4. 点击"IAT Autosearch"
5. 点击"Get Imports"
6. 点击"Dump"
7. 点击"Fix Dump"
```

---

## 🔐 反反调试技巧

### 1. 绕过IsDebuggerPresent
```cpp
// 在x64dbg中修改PEB
mov eax, fs:[0x30]  // PEB
mov byte ptr [eax+0x2], 0  // BeingDebugged = 0
```

### 2. 绕过CheckRemoteDebuggerPresent
```
1. 找到该API的地址
2. 设置断点
3. 修改返回值
4. 或者Hook该函数
```

### 3. 绕过时序检测
```
1. 找到QueryPerformanceCounter调用
2. 修改返回值，使时间差变小
3. 或者Hook该函数返回固定值
```

---

## 🎯 提取方块ID

### 成功Dump后

1. **字符串搜索**
   ```
   - 使用IDA Pro打开Dump文件
   - Shift+F12打开字符串窗口
   - 搜索关键词: "block", "item", "tile"
   - 查找方块名称和ID的对应关系
   ```

2. **交叉引用分析**
   ```
   - 找到方块名称字符串
   - 查看引用该字符串的代码
   - 分析ID赋值逻辑
   - 建立映射表
   ```

3. **动态调试确认**
   ```
   - 在关键函数设置断点
   - 放置方块触发断点
   - 查看寄存器和内存
   - 确认ID值
   ```

---

## ⚠️ 风险提示

### 1. 封号风险
- ACE会检测调试器
- 异常行为会被记录
- 建议使用小号测试

### 2. 系统风险
- 驱动级操作可能导致蓝屏
- 修改内存可能导致崩溃
- 请做好系统备份

### 3. 法律风险
- 未经授权的反编译可能违法
- 请确保在合法范围内操作
- 仅供学习研究使用

---

## 📚 参考资源

### 工具
- [x64dbg](https://x64dbg.com/)
- [Scylla](https://github.com/NtQuery/Scylla)
- [Process Hacker](https://processhacker.sourceforge.io/)
- [IDA Pro](https://hex-rays.com/ida-pro/)

### 学习资料
- 《逆向工程核心原理》
- 《加密与解密》
- 《Windows PE权威指南》

---

## 📝 总结

ACE保护虽然强大，但并非不可逾越。通过内存Dump技术，可以在代码解密后获取原始代码。关键是：

1. 找到代码解密的时机
2. 绕过反调试机制
3. 正确Dump和重建PE
4. 分析提取方块ID

**再次提醒：请在合法授权范围内使用这些技术。**

---

**文档版本**: 1.0  
**最后更新**: 2026-02-28
