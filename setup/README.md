# 环境设置指南

配置开发和测试环境的完整指南。

---

## 目录

1. [Wireshark抓包配置](wireshark_setup.md)
2. [测试账号准备](test_accounts.md)

---

## 快速设置清单

### 开发环境

- [ ] Java 17+ 安装
- [ ] Python 3.11+ 安装
- [ ] Git 安装
- [ ] IDE 配置 (VS Code / IntelliJ)

### 逆向工程工具

- [ ] apktool 2.9.3
- [ ] jadx 1.4.7
- [ ] frida-server 16.1.11
- [ ] Wireshark 4.2+

### Minecraft服务端

- [ ] PaperMC 1.20.6
- [ ] GeyserMC 2.3.1
- [ ] Floodgate
- [ ] Fabric Loader

### 测试环境

- [ ] Android 模拟器 / 真机
- [ ] Minecraft Java 客户端
- [ ] Minecraft 基岩版客户端
- [ ] 迷你世界客户端

### 网络环境

- [ ] 本地网络配置
- [ ] 端口转发（如需外网测试）
- [ ] VPN/科学上网（外服测试）

---

## 设置顺序

### 第一阶段：基础工具（10分钟）

1. 安装 Java 17
2. 安装 Python 3.11
3. 克隆项目仓库
4. 运行完整性检查

### 第二阶段：逆向工程工具（15分钟）

1. 下载 apktool
2. 下载 jadx
3. 下载 frida-server
4. 验证工具可用

### 第三阶段：服务端（10分钟）

1. 下载 PaperMC
2. 安装 GeyserMC
3. 配置服务端
4. 启动测试

### 第四阶段：APK准备（20分钟）

1. 下载迷你世界国服APK
2. 下载迷你世界外服APK（可选）
3. 启动反编译
4. 等待反编译完成

### 第五阶段：测试环境（30分钟）

1. 安装 Wireshark
2. 配置抓包过滤器
3. 申请测试账号
4. 准备测试设备

---

## 验证设置

运行以下命令验证环境：

```bash
# 检查Java
java -version

# 检查Python
python --version

# 检查组件
python check_and_fix_components.py

# 检查路径
python path_resolver.py

# 检查反编译状态
python apk_downloads/decompile_checkpoint.py status
```

---

## 故障排除

参见各具体文档的故障排除章节：
- [Wireshark故障排除](wireshark_setup.md#常见问题)
- [账号申请指南](test_accounts.md#账号安全)

---
Made with ❤️ by ZCNotFound for cross-platform gaming
