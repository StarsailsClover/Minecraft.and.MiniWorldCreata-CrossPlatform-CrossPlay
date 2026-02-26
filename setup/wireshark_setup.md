# Wireshark 抓包环境配置指南

配置 Wireshark 用于捕获 Minecraft 和迷你世界的网络数据包。

---

## 1. 安装 Wireshark

### Windows 安装

1. **下载 Wireshark**
   - 官网: https://www.wireshark.org/download.html
   - 下载 Windows Installer (64-bit)

2. **安装步骤**
   ```powershell
   # 运行安装程序
   Wireshark-win64-4.2.4.exe
   
   # 安装选项:
   # ✓ Wireshark
   # ✓ TShark (命令行版本)
   # ✓ Npcap (Windows抓包驱动)
   # ✓ USBPcap (USB抓包，可选)
   ```

3. **安装 Npcap**
   - Wireshark 安装过程中会自动安装 Npcap
   - 或单独下载: https://npcap.com/

### 验证安装

```powershell
# 检查版本
wireshark --version

# 检查接口列表
tshark -D
```

---

## 2. 配置抓包过滤器

### Minecraft Java 版过滤器

```
# 基本过滤器 - 捕获MC Java流量
tcp.port == 25565

# 包含握手和登录
(tcp.port == 25565) || (tcp.port == 25575)

# 特定IP
tcp.port == 25565 && ip.addr == 192.168.1.100
```

### Minecraft Bedrock 版过滤器

```
# UDP端口（基岩版使用UDP）
udp.port == 19132

# IPv6端口
udp.port == 19133

# 所有基岩版端口
udp.port in {19132, 19133}
```

### 迷你世界过滤器（待确认）

```
# 猜测的端口（需要抓包确认）
tcp.port == 8080
tcp.port == 443
udp.port == 8000

# 或根据服务器IP
ip.addr == 114.114.114.114  # 示例IP
```

### 组合过滤器

```
# 捕获所有游戏流量
(tcp.port == 25565) || (udp.port == 19132) || (tcp.port == 8080)

# 排除本地流量
(tcp.port == 25565) && !(ip.addr == 127.0.0.1)
```

---

## 3. 配置显示过滤器

### 常用显示过滤器

```
# 按协议筛选
minecraft
tcp
udp
http
ssl

# 按端口筛选
tcp.port == 25565
udp.port == 19132

# 按IP筛选
ip.src == 192.168.1.100
ip.dst == 114.114.114.114

# 按数据包大小
frame.len > 100

# 按时间（最近10秒）
frame.time_relative > 10
```

### Minecraft 专用过滤器

```
# 查找特定数据包类型
# 需要解析Minecraft协议后使用
minecraft.packet_id == 0x0F  # 聊天消息
minecraft.packet_id == 0x1A  # 玩家位置
```

---

## 4. 配置解密（SSL/TLS）

### 解密 HTTPS 流量

1. **设置 SSLKEYLOGFILE 环境变量**
   ```powershell
   [Environment]::SetEnvironmentVariable("SSLKEYLOGFILE", "C:\\Users\\$env:USERNAME\\ssl-keys.log", "User")
   ```

2. **在 Wireshark 中配置**
   - Edit → Preferences → Protocols → TLS
   - (Pre)-Master-Secret log filename: `C:\Users\<username>\ssl-keys.log`

---

## 5. 自动化抓包脚本

### PowerShell 抓包脚本

```powershell
# capture_minecraft.ps1

$interface = "\\Device\\NPF_{...}"  # 使用 tshark -D 查看接口ID
$outputFile = "mc_capture_$(Get-Date -Format 'yyyyMMdd_HHmmss').pcap"
$duration = 300  # 5分钟

Write-Host "开始抓包，持续 $duration 秒..."
Write-Host "输出文件: $outputFile"

# 使用 tshark 抓包
tshark -i $interface `
       -f "tcp port 25565 or udp port 19132" `
       -a duration:$duration `
       -w $outputFile

Write-Host "抓包完成: $outputFile"
```

### 使用方法

```powershell
# 运行抓包脚本
.\capture_minecraft.ps1

# 或手动抓包
tshark -i 1 -f "tcp port 25565" -w minecraft.pcap
```

---

## 6. 分析抓包结果

### 使用 Wireshark 分析

1. **打开抓包文件**
   ```
   File → Open → minecraft.pcap
   ```

2. **应用显示过滤器**
   ```
   tcp.port == 25565
   ```

3. **查看数据包详情**
   - 选择数据包
   - 查看 Packet Details 面板
   - 展开 Minecraft 协议层（如果已解析）

### 导出数据

```powershell
# 导出为 JSON
tshark -r minecraft.pcap -T json > minecraft.json

# 导出为 CSV
tshark -r minecraft.pcap -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e tcp.port -E header=y > minecraft.csv

# 导出特定数据包
tshark -r minecraft.pcap -Y "minecraft" -w minecraft_filtered.pcap
```

---

## 7. 协议分析工作流

### 完整流程

```
1. 启动抓包
   tshark -i 1 -w capture.pcap

2. 启动游戏
   - 启动 Minecraft Java/Bedrock
   - 或启动迷你世界

3. 执行操作
   - 登录
   - 移动
   - 放置/破坏方块
   - 发送聊天消息

4. 停止抓包
   Ctrl+C

5. 分析数据
   - 用 Wireshark 打开 capture.pcap
   - 应用过滤器
   - 查看数据包结构
   - 记录协议信息
```

---

## 8. 常见问题

### Q: 无法找到网络接口

**解决**:
```powershell
# 以管理员身份运行 Wireshark
# 或安装 Npcap 时选择 "Support raw 802.11 traffic"
```

### Q: 无法捕获本地流量

**解决**:
```powershell
# Windows 需要特殊配置
# 方法1: 使用 RawCap
RawCap.exe 127.0.0.1 localhost.pcap

# 方法2: 使用路由表
route add 192.168.1.100 mask 255.255.255.255 192.168.1.1 metric 1
```

### Q: 数据包显示为乱码

**原因**: Minecraft 使用自定义协议，Wireshark 默认不解析

**解决**:
1. 开发 Lua 协议解析插件
2. 或使用 Python 脚本解析原始数据

---

## 9. 下一步

配置完成后，进行实际抓包：
1. [Minecraft Java 协议抓包](../docs/mc_java_capture.md)
2. [Minecraft Bedrock 协议抓包](../docs/mc_bedrock_capture.md)
3. [迷你世界协议抓包](../docs/miniworld_capture.md)

---
Made with ❤️ by ZCNotFound for cross-platform gaming
