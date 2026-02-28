<!-- 
此文档已脱敏处理
处理时间: 2026-02-28T13:37:25.583393
原始文件: SECURITY_AUDIT_PLAN.md
-->

# 安全审计与数据脱敏计划

**时间**: 2026-02-28  
**任务**: 全面安全检查、数据脱敏、加密处理

---

## 一、未开发项检查

### 已识别的未开发项

| 模块 | 状态 | 说明 |
|------|------|------|
| DLL深度分析 | 🔄 进行中 | 需IDA Pro/Ghidra |
| 完整方块ID映射 | ⬜ 待完成 | 需29+方块精确映射 |
| Java版连接测试 | ⬜ 待完成 | 需真实服务器测试 |
| Bedrock版连接测试 | ⬜ 待完成 | 需真实服务器测试 |
| 端到端桥接测试 | ⬜ 待完成 | Java/Bedrock <-> 迷你世界 |

### 需加密/脱敏的敏感信息

#### 1. 服务器地址和端口
- `[数据处理字符:28]`
- `[数据处理字符:22]`
- `[数据处理字符:23]/19701`
- `[数据处理字符:16]`
- 其他游戏服务器IP

#### 2. API端点和认证信息
- `/auth/loginout` 及参数
- JWT Token结构
- 认证密钥和签名
- 用户UIN和AppID

#### 3. 协议细节
- 数据包结构
- 命令码定义
- 加密算法细节

---

## 二、脱敏规则

### 文档脱敏格式
```
原始: `[数据处理字符:28] /auth/loginout?uin=[数据处理字符:14]&auth=xxx`
脱敏: `[数据处理字符:28] /auth/loginout?[数据处理字符:198]`

原始: `https://example.com/api?token=abc123&secret=xyz789`
脱敏: `https://[数据处理字符:11]/api?[数据处理字符:50]`
```

### 代码加密规则
- 服务器地址: AES-256加密，运行时解密
- API密钥: 环境变量或配置文件存储
- 协议常量: 混淆处理

---

## 三、执行步骤

### Step 1: 备份所有文件
- 备份到 `MnMCPResources/backup_pre_security/`
- 保留原始文件副本

### Step 2: 文档脱敏
- 扫描所有 .md 文件
- 识别敏感信息模式
- 应用脱敏规则
- 验证脱敏效果

### Step 3: 代码加密
- 识别含敏感信息的代码文件
- 创建加密模块
- 加密敏感字符串
- 添加运行时解密逻辑

### Step 4: 更新部署脚本
- 添加解密环境初始化
- 更新启动脚本
- 测试部署流程

### Step 5: 验证
- 检查部署后是否能正常解密
- 验证功能完整性
- 确保无敏感信息泄露

---

## 四、文件清单

### 需脱敏的文档
- [ ] HANDSHAKE_ANALYSIS_REPORT.md
- [ ] HANDSHAKE_VERIFICATION_COMPLETE.md
- [ ] ProtocolAnalysisReport.md
- [ ] ProtocolImplementation.md
- [ ] 所有包含服务器地址的文档

### 需加密的代码
- [ ] src/core/protocol_translator.py
- [ ] src/core/proxy_server.py
- [ ] src/protocol/login_handler.py
- [ ] 所有包含服务器配置的代码

---

## 五、加密方案

### 加密算法
- 算法: AES-256-GCM
- 密钥: 从环境变量或配置文件读取
- 密文存储: Base64编码

### 运行时解密
```python
# 示例
from security.crypto import decrypt

# 加密的数据
SERVER_HOST = decrypt("ENC:xxx...")
API_ENDPOINT = decrypt("ENC:yyy...")
```

### 部署时解密
- 启动脚本加载密钥
- 初始化解密环境
- 运行时透明解密

---

## 六、检查清单

- [ ] 所有敏感信息已脱敏
- [ ] 所有敏感代码已加密
- [ ] 备份文件已创建
- [ ] 部署脚本已更新
- [ ] 解密功能已验证
- [ ] 项目可以正常部署和运行
