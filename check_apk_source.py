#!/usr/bin/env python3
"""
检查APK来源（官服 vs 渠道服）
"""

import os
import sys
import zipfile
from pathlib import Path

# 动态获取路径
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
EXTERNAL_DIR = Path(r"C:\Users\Sails\Documents\Coding\MnMCPResources")

APK_PATH = EXTERNAL_DIR / "apk_downloads" / "miniworld_cn_1.53.1.apk"

def check_apk_exists():
    """检查APK是否存在"""
    if not APK_PATH.exists():
        print(f"✗ APK不存在: {APK_PATH}")
        return False
    
    size_gb = APK_PATH.stat().st_size / 1024 / 1024 / 1024
    print(f"✓ APK存在")
    print(f"  路径: {APK_PATH}")
    print(f"  大小: {size_gb:.2f} GB")
    return True

def check_channel_indicators():
    """检查渠道服标识"""
    print("\n[检查渠道标识]")
    
    channel_indicators = {
        "官服标识": [
            "com.minitech.miniworld",  # 官方包名
            "assets/official",          # 官方资源
        ],
        "华为渠道": [
            "com.huawei",
            "hms",                      # 华为移动服务
            "华为", "huawei",
        ],
        "小米渠道": [
            "com.xiaomi",
            "xiaomi", "小米",
        ],
        "OPPO渠道": [
            "com.oppo",
            "oppo", "nearme",
        ],
        "vivo渠道": [
            "com.vivo",
            "vivo",
        ],
        "应用宝": [
            "com.tencent",
            "应用宝",
        ],
        "九游": [
            "com.uc",
            "九游", "uc",
        ],
        "百度": [
            "com.baidu",
            "百度",
        ],
        "360": [
            "com.qihoo",
            "360",
        ],
    }
    
    found_channels = []
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            file_list = zf.namelist()
            
            # 检查AndroidManifest.xml
            manifest_content = ""
            if "AndroidManifest.xml" in file_list:
                try:
                    manifest_content = zf.read("AndroidManifest.xml").decode('utf-8', errors='ignore')
                except:
                    pass
            
            # 检查各渠道标识
            for channel, indicators in channel_indicators.items():
                found = False
                for indicator in indicators:
                    # 检查文件名
                    for filename in file_list:
                        if indicator.lower() in filename.lower():
                            found = True
                            break
                    
                    # 检查manifest内容
                    if not found and indicator.lower() in manifest_content.lower():
                        found = True
                    
                    if found:
                        break
                
                if found:
                    found_channels.append(channel)
                    print(f"  ⚠ 发现 {channel} 标识")
    
    except Exception as e:
        print(f"  ✗ 检查失败: {str(e)}")
        return []
    
    return found_channels

def check_package_name():
    """检查包名"""
    print("\n[检查包名]")
    
    official_package = "com.minitech.miniworld"
    
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            # 读取AndroidManifest.xml
            if "AndroidManifest.xml" in zf.namelist():
                content = zf.read("AndroidManifest.xml").decode('utf-8', errors='ignore')
                
                # 查找包名
                import re
                match = re.search(r'package="([^"]+)"', content)
                if match:
                    package_name = match.group(1)
                    print(f"  包名: {package_name}")
                    
                    if package_name == official_package:
                        print(f"  ✓ 官方包名匹配")
                        return True
                    else:
                        print(f"  ⚠ 包名不匹配官方包名")
                        print(f"    官方: {official_package}")
                        return False
                else:
                    print(f"  ✗ 无法解析包名")
                    return False
            else:
                print(f"  ✗ AndroidManifest.xml 不存在")
                return False
    
    except Exception as e:
        print(f"  ✗ 检查失败: {str(e)}")
        return False

def check_signature():
    """检查签名信息"""
    print("\n[检查签名信息]")
    print("  注意: 需要apktool或jarsigner工具")
    print("  官服签名: CN=Miniwan, OU=Miniwan, O=Miniwan Technology")
    
    # 检查META-INF目录
    try:
        with zipfile.ZipFile(APK_PATH, 'r') as zf:
            meta_files = [f for f in zf.namelist() if f.startswith("META-INF/")]
            
            if meta_files:
                print(f"  签名文件数: {len(meta_files)}")
                for f in meta_files[:5]:  # 显示前5个
                    print(f"    - {f}")
            else:
                print("  ✗ 未找到签名文件")
    
    except Exception as e:
        print(f"  ✗ 检查失败: {str(e)}")

def print_recommendation(found_channels):
    """打印建议"""
    print("\n" + "="*70)
    print("检查结果分析")
    print("="*70)
    
    if not found_channels:
        print("✓ 未发现明显的渠道服标识")
        print("  可能是官方包，建议进一步验证签名")
    elif "官服标识" in found_channels and len(found_channels) == 1:
        print("✓ 疑似官方包")
        print("  发现官方包名标识")
    else:
        print("⚠ 疑似渠道服")
        print(f"  发现渠道标识: {', '.join(found_channels)}")
        print("\n建议:")
        print("1. 从官网 https://www.mini1.cn/ 重新下载")
        print("2. 确保下载的是'官方安卓版'而非应用商店版本")
        print("3. 重新进行反编译")

def main():
    """主函数"""
    print("="*70)
    print("迷你世界APK来源检查工具")
    print("="*70)
    
    # 检查APK
    if not check_apk_exists():
        return
    
    # 检查包名
    is_official_package = check_package_name()
    
    # 检查渠道标识
    found_channels = check_channel_indicators()
    
    # 检查签名
    check_signature()
    
    # 打印建议
    print_recommendation(found_channels)
    
    print("\n" + "="*70)
    print("检查完成")
    print("="*70)

if __name__ == "__main__":
    main()
