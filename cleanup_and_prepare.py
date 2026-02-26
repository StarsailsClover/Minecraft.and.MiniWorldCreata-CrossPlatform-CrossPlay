#!/usr/bin/env python3
"""
清理旧文件并准备官方APK下载
"""

import os
import shutil
from pathlib import Path

# 路径配置
PROJECT_DIR = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay")
EXTERNAL_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources")

OLD_APK = EXTERNAL_DIR / "apk_downloads" / "miniworld_cn_1.53.1.apk"
NEW_APK = EXTERNAL_DIR / "apk_downloads" / "miniworld_cn_official_1.53.1.apk"
DECOMPILE_OUTPUT = EXTERNAL_DIR / "apk_downloads" / "miniworld_cn_decompiled"
CHECKPOINT_FILE = PROJECT_DIR / "reverse_engineering" / "decompile_checkpoint.json"
LOG_FILE = PROJECT_DIR / "reverse_engineering" / "decompile_log.txt"

def print_header():
    print("="*70)
    print("清理旧文件并准备官方APK下载")
    print("="*70)

def stop_decompilation():
    """停止反编译进程"""
    print("\n[1/5] 停止反编译进程")
    
    import subprocess
    try:
        # 查找并停止Java进程
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process -Name java -ErrorAction SilentlyContinue | '
             'Where-Object {$_.CommandLine -like \'*decompile_checkpoint*\'} | '
             'Stop-Process -Force'],
            capture_output=True,
            text=True
        )
        print("  ✓ 已停止反编译进程")
    except Exception as e:
        print(f"  ⚠ 停止进程时出错: {e}")

def delete_decompile_output():
    """删除反编译输出"""
    print("\n[2/5] 删除反编译输出")
    
    if DECOMPILE_OUTPUT.exists():
        try:
            shutil.rmtree(DECOMPILE_OUTPUT)
            print(f"  ✓ 已删除: {DECOMPILE_OUTPUT}")
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")
    else:
        print(f"  ℹ 目录不存在: {DECOMPILE_OUTPUT}")

def reset_checkpoint():
    """重置检查点"""
    print("\n[3/5] 重置检查点")
    
    if CHECKPOINT_FILE.exists():
        try:
            CHECKPOINT_FILE.unlink()
            print(f"  ✓ 已删除: {CHECKPOINT_FILE}")
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")
    else:
        print(f"  ℹ 检查点文件不存在")
    
    if LOG_FILE.exists():
        try:
            LOG_FILE.unlink()
            print(f"  ✓ 已删除: {LOG_FILE}")
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")

def backup_old_apk():
    """备份旧APK"""
    print("\n[4/5] 备份旧APK（渠道服）")
    
    if OLD_APK.exists():
        backup_dir = EXTERNAL_DIR / "apk_downloads" / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / "miniworld_cn_channel_1.53.1.apk"
        
        try:
            shutil.move(str(OLD_APK), str(backup_path))
            print(f"  ✓ 已备份到: {backup_path}")
            print(f"  ℹ 旧APK为渠道服，已备份保留")
        except Exception as e:
            print(f"  ✗ 备份失败: {e}")
    else:
        print(f"  ℹ 旧APK不存在")

def create_download_guide():
    """创建下载指南"""
    print("\n[5/5] 创建官方APK下载指南")
    
    guide_content = f"""
# 官方APK下载指南

## 下载目标
- **文件名**: miniworld_cn_official_1.53.1.apk
- **保存路径**: {NEW_APK}
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
- 保存位置: {EXTERNAL_DIR / 'apk_downloads'}

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
Generated: {__import__('datetime').datetime.now().isoformat()}
"""
    
    guide_file = PROJECT_DIR / "apk_downloads" / "DOWNLOAD_OFFICIAL_APK_NOW.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"  ✓ 已创建: {guide_file}")

def print_summary():
    """打印总结"""
    print("\n" + "="*70)
    print("清理完成")
    print("="*70)
    
    print("\n[下一步]")
    print("1. 访问 https://www.mini1.cn/")
    print("2. 下载官方安卓版APK")
    print(f"3. 保存为: {NEW_APK.name}")
    print(f"4. 保存到: {NEW_APK.parent}")
    
    print("\n[验证]")
    print("下载完成后，运行:")
    print("  python check_apk_source.py")
    
    print("\n[反编译]")
    print("验证通过后，运行:")
    print("  python decompile_checkpoint.py")

def main():
    print_header()
    
    stop_decompilation()
    delete_decompile_output()
    reset_checkpoint()
    backup_old_apk()
    create_download_guide()
    
    print_summary()

if __name__ == "__main__":
    main()
