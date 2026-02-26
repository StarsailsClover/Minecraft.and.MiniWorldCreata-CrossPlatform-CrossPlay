# 迷你世界官方包下载指南

当前APK疑似包含渠道服标识，需要从官网重新下载官方包。

---

## 问题分析

### 当前APK检查结果
- **文件**: miniworld_cn_1.53.1.apk
- **大小**: 1.60 GB
- **问题**: 发现多个渠道标识
  - 华为渠道
  - OPPO渠道
  - 应用宝
  - 九游

**结论**: 当前APK可能是渠道服或聚合包，不是纯净的官方包。

---

## 官方包下载步骤

### 方法1: 官网下载（推荐）

1. **访问官网**
   ```
   https://www.mini1.cn/
   ```

2. **找到下载入口**
   - 首页点击"下载游戏"或"安卓下载"
   - 确保选择的是"官方安卓版"
   - **不要**选择应用商店版本

3. **确认下载链接**
   - 官方下载链接通常包含 `mini1.cn` 域名
   - 示例: `https://app.mini1.cn/export/down_app/1`

4. **保存文件**
   - 文件名: `miniworld_cn_official_1.53.1.apk`
   - 保存路径: `C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\`

### 方法2: 官方论坛

1. 访问迷你世界官方论坛
2. 查找"官方包下载"帖子
3. 从官方链接下载

### 方法3: 联系客服

如果无法确定下载链接，可以：
1. 联系迷你世界官方客服
2. 询问官方APK下载地址
3. 确认包名: `com.minitech.miniworld`

---

## 验证官方包

### 检查包名
```bash
# 使用aapt（Android SDK工具）
aapt dump badging miniworld_cn_official_1.53.1.apk | findstr "package"

# 应该显示: package: name='com.minitech.miniworld'
```

### 检查签名
```bash
# 使用apktool
apktool d miniworld_cn_official_1.53.1.apk -o verify_temp
cat verify_temp/original/META-INF/CERT.RSA

# 或使用jarsigner
jarsigner -verify -verbose -certs miniworld_cn_official_1.53.1.apk
```

### 官方签名特征
- **CN**: Miniwan
- **OU**: Miniwan
- **O**: Miniwan Technology

---

## 重新反编译

下载官方包后，重新进行反编译：

```bash
# 1. 停止当前反编译（如果还在运行）
# 2. 删除旧的反编译输出
rd /s /q C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_decompiled

# 3. 重置检查点
python decompile_checkpoint.py reset

# 4. 更新反编译脚本中的APK路径
# 编辑 decompile_checkpoint.py，更新APK_NAME

# 5. 重新启动反编译
python decompile_checkpoint.py
```

---

## 渠道服 vs 官服区别

| 特性 | 官服 | 渠道服 |
|------|------|--------|
| 包名 | com.minitech.miniworld | 可能不同 |
| 登录方式 | 迷你号/手机号 | 渠道账号 |
| 服务器 | 官方服务器 | 渠道服务器 |
| 充值 | 官方充值 | 渠道充值 |
| 协议 | 标准协议 | 可能有渠道定制 |
| 逆向价值 | 高（标准协议） | 低（渠道定制） |

**为什么需要官服？**
1. 渠道服可能有渠道特定的SDK和协议
2. 官服协议更标准，逆向价值更高
3. 渠道服可能有额外的加密或验证
4. 我们需要分析的是官方标准协议

---

## 注意事项

1. **不要从应用商店下载**
   - 华为应用市场
   - 小米应用商店
   - OPPO/vivo应用商店
   - 应用宝
   - 这些通常都是渠道服

2. **认准官网域名**
   - 正确: mini1.cn
   - 错误: 其他域名或应用商店链接

3. **文件大小参考**
   - 官服: ~1.5-1.8 GB
   - 渠道服: 可能更大（包含渠道SDK）

---

## 下一步

1. ⬜ 从官网下载官方APK
2. ⬜ 验证包名和签名
3. ⬜ 停止当前反编译
4. ⬜ 删除旧反编译输出
5. ⬜ 重新启动反编译
6. ⬜ 更新文档记录

---
Made with ❤️ by ZCNotFound for cross-platform gaming
