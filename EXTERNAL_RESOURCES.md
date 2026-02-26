# 外部资源目录

由于文件大小限制（>100MB），以下资源存储在外部目录：

## 外部目录位置
```
C:\Users\Sails\Documents\Coding\MnMCPResources
```

## 目录结构
```
MnMCPResources/
├── server/          # 服务端文件（预留）
├── tools/           # 工具文件（预留）
└── apk_downloads/   # APK文件
    └── miniworld_cn_1.53.1.apk    # 迷你世界国服 (1.60 GB)
```

## 已移动的文件

| 原位置 | 新位置 | 大小 | 说明 |
|--------|--------|------|------|
| apk_downloads/miniworld_cn_latest.apk | MnMCPResources/apk_downloads/miniworld_cn_1.53.1.apk | 1.60 GB | 迷你世界国服APK |

## 如何访问

原始位置的文件已被替换为：
- `.location` 文件 - 记录实际存储位置

例如：
```
apk_downloads/miniworld_cn_1.53.1.apk.location
内容：
FILE_MOVED_TO:
C:\Users\Sails\Documents\Coding\MnMCPResources\apk_downloads\miniworld_cn_1.53.1.apk
```

## 使用说明

在脚本中访问资源时，使用以下方式：

```python
# 读取位置文件获取实际路径
with open('apk_downloads/miniworld_cn_1.53.1.apk.location', 'r') as f:
    lines = f.readlines()
    actual_path = lines[1].strip()

# 现在可以使用 actual_path 访问文件
```

## 注意事项

1. 不要手动移动外部目录中的文件
2. 如需添加新的大文件，使用 `move_large_files.py` 脚本
3. 外部目录与项目目录保持同步备份

---
Made with ❤️ by ZCNotFound for cross-platform gaming
