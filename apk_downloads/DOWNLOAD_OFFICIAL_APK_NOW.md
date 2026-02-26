
# 官方APK下载指南

## 下载目标
- **文件名**: miniworld_cn_official_1.53.1.apk
- **保存路径**: C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_official_1.53.1.apk
- **大小**: ~1.5-1.8 GB

## 下载步骤

### 1. 访问官网
打开浏览器访问: https://www.mini1.cn/

### 2. 找到下载入口
- 在首页找到"下载游戏"或"安卓下载"按钮
- **注意**: 选择"官方安卓版"，不要选择应用商店版本

### 3. 确认下载链接
- 官方链接域名应包含: mini1.cn
- 示例: https://app.mini1.cn/export/down_app/1

### 4. 保存文件
- 将下载的文件保存为: miniworld_cn_official_1.53.1.apk
- 保存位置: C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads

## 验证官方包

### 检查包名
```bash
# 使用apktool
apktool d miniworld_cn_official_1.53.1.apk -o verify_temp

# 查看AndroidManifest.xml
# 应该包含: package="com.minitech.miniworld"
```

### 检查签名
官方签名信息:
- CN: Miniwan
- OU: Miniwan
- O: Miniwan Technology

## 下载完成后

1. 运行清理脚本确认新APK
2. 启动新的反编译任务
3. 开始协议分析

## 注意事项

⚠️ **不要从以下渠道下载**:
- 华为应用市场
- 小米应用商店
- OPPO/vivo应用商店
- 应用宝
- 九游
- 其他第三方应用商店

✅ **正确的下载来源**:
- 官网: https://www.mini1.cn/
- 官方论坛
- 官方客服提供的链接

---
Generated: 2026-02-26T09:32:33.003412
