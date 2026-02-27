# MnMCP 测试环境配置指南

**日期**: 2026-02-27  
**版本**: Step 2.1

---

## 已启动的组件

### ✅ 1. 迷你世界客户端
- **状态**: 已启动
- **路径**: `C:\Users\Sails\Documents\Coding\MnMCPResources\packs_downloads\miniworldPC_CN\miniworldLauncher\MicroMiniNew.exe`
- **操作**: 请在迷你世界启动器中登录并进入游戏

### ✅ 2. 代理服务器
- **状态**: 就绪
- **端口**: 25565
- **功能**: 监听Minecraft客户端连接

---

## 测试步骤

### 步骤 1: 配置迷你世界代理（可选）

如果你想通过代理捕获迷你世界流量：

1. 打开 **Proxifier**（如果在D盘找到）
2. 添加规则：将 `MicroMiniNew.exe` 的流量转发到代理
3. 或者使用系统代理设置

### 步骤 2: 启动网络监控

```bash
python network_monitor.py
```

这将启动一个带监控的代理服务器，可以：
- 捕获数据包
- 分析协议类型
- 记录流量统计

### 步骤 3: 启动Minecraft客户端

1. 打开Minecraft 1.20.6
2. 添加服务器：
   - 服务器地址: `localhost:25565`
   - 服务器名称: `MnMCP Test`
3. 连接服务器

### 步骤 4: 观察数据流

在控制台观察：
- Minecraft客户端发送的数据包
- 代理服务器的处理日志
- 协议分析和统计

---

## 抓包分析

### 方法 1: 使用网络监控代理
```bash
python network_monitor.py
```

### 方法 2: 使用 Windows 网络监控
```powershell
# 查看网络连接
netstat -an | findstr 25565

# 查看进程网络活动
Get-NetTCPConnection -LocalPort 25565
```

### 方法 3: 使用内置工具
运行 `test_client.py` 模拟Minecraft客户端：
```bash
python test_client.py
```

---

## 预期结果

### 正常情况
```
✅ 代理服务器启动成功
✅ Minecraft客户端连接成功
✅ 数据包传输正常
✅ 协议识别正确
```

### 数据包示例
```
[数据包] 长度: 17 | MC: True | MNW: False
[数据] 001000096c6f63616c686f737463dd016402...
```

---

## 故障排除

### 问题 1: 端口被占用
```powershell
# 查找占用25565端口的进程
netstat -ano | findstr 25565

# 结束进程
taskkill /PID <进程ID> /F
```

### 问题 2: 连接被拒绝
- 检查防火墙设置
- 确保代理服务器已启动
- 检查IP地址和端口

### 问题 3: 数据包解析错误
- 检查Minecraft版本（应为1.20.6）
- 查看详细日志
- 确认协议版本匹配

---

## 下一步

1. **捕获真实数据** - 让Minecraft客户端通过代理连接
2. **分析协议** - 根据捕获的数据调整协议翻译
3. **连接MNW** - 将数据转发到真实迷你世界服务器
4. **验证功能** - 测试方块同步、聊天等功能

---

## 注意事项

1. **安全性**: 不要在生产环境使用测试代理
2. **性能**: 测试代理未优化，仅用于开发调试
3. **数据**: 捕获的数据可能包含敏感信息，注意保护
4. **法律**: 遵守相关服务条款和法律法规
