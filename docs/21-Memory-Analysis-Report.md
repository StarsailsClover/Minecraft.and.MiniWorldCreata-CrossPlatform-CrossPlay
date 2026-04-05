# 迷你世界内存提取 - 技术分析报告 (脱敏版)

**分析日期**: 2026-03-14  
**来源**: VMware vmem 内存镜像  
**版本**: 79105

---

## 1. 认证体系分析

### JWT Token 结构
- **算法**: HS256
- **签发者**: imserver (生产环境 chatpush 服务)
- **有效期**: 30 天
- **Payload 字段**:
  - `uin`: 用户迷你号
  - `time`: 签发时间 (Unix 时间戳)
  - `exp`: 过期时间
  - `flag`: 标志位
  - `iss`: 签发者

### 认证流程
```
1. HTTPS certification.mini1.cn:19921/login
   → 提交: uin + password_hash(MD5) + device_id
   ← 返回: JWT Token

2. HTTPS openroom.mini1.cn:8080/alloc
   → 提交: JWT Token
   ← 返回: game_server_ip + port

3. TCP game_server:4012
   → LOGIN_REQ (3001) + JWT
   ← LOGIN_RESP (3002) + session_key
   → 激活 AES-128-CBC 加密

4. WebSocket chatpush.mini1.cn:19701
   → JWT 认证
   ← 聊天消息推送
```

### Sign 签名算法
```
sign = md5(参数拼接 + appkey) + "_" + timestamp
```

- **signType 类型**:
  - `md5`: 标准 MD5 签名
  - `client_ext`: 客户端扩展签名
  - `client`: 客户端签名

---

## 2. 加密体系

### 通信加密
- **国服**: AES-128-CBC
- **密钥交换**: ECDH (DHKeyMgr)
- **Lua 接口**:
  - `GenerateClientDHKey()`
  - `GenerateServerDHKey()`

### XXTEA
- 用于资源文件加密
- 密钥从内存中提取 (已脱敏处理)

---

## 3. 网络架构

### 服务器地址
| 服务 | 地址 | 端口 | 协议 |
|------|------|------|------|
| 认证 | certification.mini1.cn | 19921 | HTTPS |
| 房间分配 | openroom.mini1.cn | 8080 | HTTPS |
| 游戏服务器 | cn-logic{N}.mini1.cn | 4012 | TCP |
| 聊天推送 | chatpush.mini1.cn | 19701 | WebSocket |

---

## 4. 安全发现

### VMProtect 保护
- 部分 DLL 使用 VMProtect 加壳
- 增加逆向分析难度
- 核心算法在虚拟机中执行

### 敏感信息处理
- 所有 JWT Token、授权码、UIN 已脱敏
- 仅保留算法和流程分析

---

## 参考

- 完整内存 dump: `MnMCPResources/dumpingmem/2603140044/` (私有)
- PKG 解包工具: `MnMCPResources/tools/pkg_unpacker.py`
