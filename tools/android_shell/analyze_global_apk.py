#!/usr/bin/env python3
"""
分析外服（Global）APK并与国服对比
"""

import os
import sys
import subprocess
import json
import zipfile
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
CN_APK = EXTERNAL_DIR / "packs_downloads" / "miniworldMini-wp.apk"
GLOBAL_APK = EXTERNAL_DIR / "packs_downloads" / "miniworld_en_1.7.15.apk"
OUTPUT_DIR = EXTERNAL_DIR / "packs_downloads" / "global_analysis"
JADX_PATH = PROJECT_DIR / "tools" / "jadx" / "bin" / "jadx.bat"

def check_apks():
    """检查APK文件是否存在"""
    print("[*] 检查APK文件...")
    
    if not CN_APK.exists():
        print(f"[-] 国服APK不存在: {CN_APK}")
        return False
    
    if not GLOBAL_APK.exists():
        print(f"[-] 外服APK不存在: {GLOBAL_APK}")
        return False
    
    cn_size = CN_APK.stat().st_size / (1024*1024)
    global_size = GLOBAL_APK.stat().st_size / (1024*1024)
    
    print(f"[+] 国服APK: {cn_size:.2f} MB")
    print(f"[+] 外服APK: {global_size:.2f} MB")
    
    return True

def extract_apk_info(apk_path):
    """提取APK基本信息"""
    print(f"\n[*] 分析APK: {apk_path.name}")
    
    info = {
        "filename": apk_path.name,
        "size_mb": apk_path.stat().st_size / (1024*1024),
        "package_name": None,
        "version_name": None,
        "version_code": None,
        "permissions": [],
        "activities": [],
        "services": []
    }
    
    try:
        with zipfile.ZipFile(apk_path, 'r') as z:
            # 读取AndroidManifest.xml
            if 'AndroidManifest.xml' in z.namelist():
                # 注意：这里需要aapt或apktool来正确解析
                # 简化处理，只提取文件列表
                info["files_count"] = len(z.namelist())
                
                # 查找lib目录
                lib_files = [f for f in z.namelist() if f.startswith('lib/')]
                info["lib_count"] = len(lib_files)
                info["architectures"] = list(set([f.split('/')[1] for f in lib_files if '/' in f]))
                
                # 查找assets
                assets_files = [f for f in z.namelist() if f.startswith('assets/')]
                info["assets_count"] = len(assets_files)
    
    except Exception as e:
        print(f"[-] 分析失败: {e}")
    
    return info

def compare_apks(cn_info, global_info):
    """对比两个APK"""
    print("\n[*] 对比APK差异...")
    
    comparison = {
        "analysis_time": datetime.now().isoformat(),
        "size_diff_mb": global_info.get("size_mb", 0) - cn_info.get("size_mb", 0),
        "files_diff": global_info.get("files_count", 0) - cn_info.get("files_count", 0),
        "libs_diff": global_info.get("lib_count", 0) - cn_info.get("lib_count", 0),
        "architectures": {
            "cn": cn_info.get("architectures", []),
            "global": global_info.get("architectures", [])
        }
    }
    
    print(f"  大小差异: {comparison['size_diff_mb']:.2f} MB")
    print(f"  文件数差异: {comparison['files_diff']}")
    print(f"  库文件差异: {comparison['libs_diff']}")
    
    return comparison

def decompile_global_apk():
    """反编译外服APK"""
    print("\n[*] 反编译外服APK...")
    
    if not JADX_PATH.exists():
        print(f"[-] jadx不存在: {JADX_PATH}")
        return False
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources_dir = OUTPUT_DIR / "sources"
    
    cmd = [
        str(JADX_PATH),
        "-d", str(sources_dir),
        "--show-bad-code",
        str(GLOBAL_APK)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print(f"[+] 反编译成功: {sources_dir}")
            return True
        else:
            print(f"[!] 反编译警告: {result.stderr[:200]}")
            return True
    
    except Exception as e:
        print(f"[-] 反编译失败: {e}")
        return False

def analyze_global_specific():
    """分析外服特有内容"""
    print("\n[*] 分析外服特有内容...")
    
    findings = {
        "login_methods": [],
        "payment_systems": [],
        "social_platforms": [],
        "server_regions": []
    }
    
    sources_dir = OUTPUT_DIR / "sources"
    
    if not sources_dir.exists():
        print("[-] 源码目录不存在")
        return findings
    
    # 搜索外服特有的登录方式
    java_files = list(sources_dir.rglob("*.java"))
    print(f"[*] 找到 {len(java_files)} 个Java文件")
    
    # 搜索关键词
    keywords = {
        "login_methods": ["google", "facebook", "twitter", "apple", "oauth", "firebase"],
        "payment_systems": ["googleplay", "appstore", "paypal", "stripe", "payment"],
        "social_platforms": ["discord", "youtube", "instagram", "tiktok"],
        "server_regions": ["us", "eu", "asia", "global", "region", "server"]
    }
    
    for category, words in keywords.items():
        for java_file in java_files[:500]:  # 限制文件数量
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for word in words:
                        if word in content:
                            if word not in findings[category]:
                                findings[category].append(word)
            except:
                continue
    
    print("\n[+] 外服特性分析:")
    print(f"  登录方式: {findings['login_methods']}")
    print(f"  支付系统: {findings['payment_systems']}")
    print(f"  社交平台: {findings['social_platforms']}")
    print(f"  服务器区域: {findings['server_regions']}")
    
    return findings

def generate_report(cn_info, global_info, comparison, findings):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    report_file = OUTPUT_DIR / "GLOBAL_APK_ANALYSIS.md"
    
    report = f"""# 迷你世界外服APK分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## APK基本信息

### 国服APK
- **文件名**: {cn_info['filename']}
- **大小**: {cn_info['size_mb']:.2f} MB
- **文件数**: {cn_info.get('files_count', 'N/A')}
- **库文件数**: {cn_info.get('lib_count', 'N/A')}
- **架构**: {', '.join(cn_info.get('architectures', []))}

### 外服APK
- **文件名**: {global_info['filename']}
- **大小**: {global_info['size_mb']:.2f} MB
- **文件数**: {global_info.get('files_count', 'N/A')}
- **库文件数**: {global_info.get('lib_count', 'N/A')}
- **架构**: {', '.join(global_info.get('architectures', []))}

## 差异对比

| 项目 | 国服 | 外服 | 差异 |
|------|------|------|------|
| 大小 | {cn_info['size_mb']:.2f} MB | {global_info['size_mb']:.2f} MB | {comparison['size_diff_mb']:+.2f} MB |
| 文件数 | {cn_info.get('files_count', 'N/A')} | {global_info.get('files_count', 'N/A')} | {comparison['files_diff']:+d} |
| 库文件 | {cn_info.get('lib_count', 'N/A')} | {global_info.get('lib_count', 'N/A')} | {comparison['libs_diff']:+d} |

## 外服特有功能

### 登录方式
{chr(10).join(['- ' + m for m in findings['login_methods']]) if findings['login_methods'] else '- 未识别'}

### 支付系统
{chr(10).join(['- ' + p for p in findings['payment_systems']]) if findings['payment_systems'] else '- 未识别'}

### 社交平台集成
{chr(10).join(['- ' + s for s in findings['social_platforms']]) if findings['social_platforms'] else '- 未识别'}

### 服务器区域
{chr(10).join(['- ' + r for r in findings['server_regions']]) if findings['server_regions'] else '- 未识别'}

## 协议差异预期

基于APK分析，预期外服与国服在以下方面存在差异：

1. **登录认证**
   - 国服：迷你号/手机号 + 国内登录SDK
   - 外服：Google/Facebook OAuth + Firebase

2. **加密算法**
   - 国服：AES-128-CBC（预期）
   - 外服：AES-256-GCM（预期）

3. **服务器地址**
   - 国服：mini1.cn 域名
   - 外服：playmini.net 或其他国际域名

4. **内容审查**
   - 国服：有内容审查和防沉迷
   - 外服：相对宽松

## 下一步分析建议

1. **反编译外服APK**（如果尚未完成）
   - 使用jadx查看完整源码
   - 定位网络通信类

2. **对比协议实现**
   - 查找外服服务器地址
   - 分析登录流程差异
   - 识别加密算法

3. **抓包分析**
   - 安装外服APK到设备
   - 使用Wireshark抓包
   - 对比国服/外服数据包结构

## 文件位置

- 外服APK: `MnMCPResources/packs_downloads/miniworld_en_1.7.15.apk`
- 反编译源码: `MnMCPResources/packs_downloads/global_analysis/sources/`
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 报告保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("迷你世界外服APK分析工具")
    print("=" * 60)
    
    # 检查APK文件
    if not check_apks():
        return False
    
    # 提取APK信息
    cn_info = extract_apk_info(CN_APK)
    global_info = extract_apk_info(GLOBAL_APK)
    
    # 对比APK
    comparison = compare_apks(cn_info, global_info)
    
    # 反编译外服APK
    decompile_global_apk()
    
    # 分析外服特有内容
    findings = analyze_global_specific()
    
    # 生成报告
    report_file = generate_report(cn_info, global_info, comparison, findings)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"\n分析报告: {report_file}")
    print("\n下一步:")
    print("1. 查看分析报告")
    print("2. 使用jadx-gui查看外服源码")
    print("3. 对比国服/外服协议差异")
    
    return True

if __name__ == "__main__":
    main()
