#!/usr/bin/env python3
"""
APK下载脚本
用于下载逆向工程所需的APK文件
"""

import urllib.request
import urllib.error
import os
import sys
import ssl

# 禁用SSL验证（某些下载源需要）
ssl._create_default_https_context = ssl._create_unverified_context

# APK下载配置
APK_SOURCES = {
    "miniworld_cn": {
        "name": "迷你世界国服",
        "version": "1.53.1",
        "urls": [
            "https://app.mini1.cn/export/down_app/1",  # 官方下载
            "https://cdn.mini1.cn/miniworld/1.53.1/miniworld_cn_1.53.1.apk",  # 备用CDN
        ],
        "filename": "miniworld_cn_1.53.1.apk",
        "package": "com.minitech.miniworld",
    },
    "miniworld_en": {
        "name": "MiniWorld: Creata",
        "version": "1.7.15",
        "urls": [
            "https://d.apkpure.com/b/APK/com.playmini.miniworld?version=1.7.15",  # APKPure
            "https://download.apkpure.com/b/APK/com.playmini.miniworld?version=1.7.15",
        ],
        "filename": "miniworld_en_1.7.15.apk",
        "package": "com.playmini.miniworld",
    },
    "minecraft_bedrock": {
        "name": "Minecraft Bedrock",
        "version": "1.20.60",
        "urls": [
            # 注意：需要正版授权
            "https://play.google.com/store/apps/details?id=com.mojang.minecraftpe",
        ],
        "filename": "minecraft_bedrock_1.20.60.apk",
        "package": "com.mojang.minecraftpe",
        "note": "需要从Google Play Store购买下载"
    }
}

def download_file(url, output_path, timeout=120):
    """下载文件"""
    print(f"[下载] {url}")
    print(f"[目标] {output_path}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        
        # 创建opener处理重定向
        opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler,
            urllib.request.HTTPSHandler(context=ssl.create_default_context())
        )
        
        with opener.open(req, timeout=timeout) as response:
            # 获取文件名
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"\'')
            else:
                filename = os.path.basename(output_path)
            
            # 检查内容类型
            content_type = response.headers.get('Content-Type', '')
            print(f"[类型] {content_type}")
            
            # 读取数据
            data = response.read()
            file_size = len(data)
            print(f"[大小] {file_size / 1024 / 1024:.2f} MB")
            
            # 保存文件
            with open(output_path, 'wb') as f:
                f.write(data)
            
            print(f"[成功] 已保存到 {output_path}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"[错误] HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"[错误] URL错误: {e.reason}")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False

def download_apk(apk_key, output_dir="."):
    """下载指定APK"""
    if apk_key not in APK_SOURCES:
        print(f"[错误] 未知的APK: {apk_key}")
        return False
    
    apk_info = APK_SOURCES[apk_key]
    print(f"\n{'='*60}")
    print(f"[任务] 下载 {apk_info['name']} v{apk_info['version']}")
    print(f"[包名] {apk_info['package']}")
    print(f"{'='*60}")
    
    output_path = os.path.join(output_dir, apk_info['filename'])
    
    # 检查是否已存在
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"[提示] 文件已存在 ({file_size:.2f} MB)，跳过下载")
        return True
    
    # 尝试所有URL
    for url in apk_info['urls']:
        if download_file(url, output_path):
            return True
        print("[重试] 尝试下一个下载源...")
    
    print(f"[失败] 所有下载源均失败")
    return False

def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("="*60)
    print("APK下载工具")
    print("用于Minecraft与迷你世界协议逆向工程")
    print("="*60)
    
    # 显示可用APK列表
    print("\n[可用APK列表]")
    for key, info in APK_SOURCES.items():
        print(f"  {key}: {info['name']} v{info['version']}")
        if 'note' in info:
            print(f"    注意: {info['note']}")
    
    # 下载所有APK
    print("\n[开始下载所有APK]")
    results = {}
    
    for key in APK_SOURCES:
        success = download_apk(key, script_dir)
        results[key] = success
        print()
    
    # 显示结果
    print("\n" + "="*60)
    print("[下载结果汇总]")
    print("="*60)
    for key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {APK_SOURCES[key]['name']}: {status}")
    
    # 提示手动下载
    print("\n[手动下载指南]")
    print("如果自动下载失败，请手动下载以下APK:")
    print("1. 迷你世界国服 1.53.1:")
    print("   - 访问: https://www.mini1.cn/")
    print("   - 点击'安卓下载'按钮")
    print("   - 保存为: miniworld_cn_1.53.1.apk")
    print()
    print("2. MiniWorld: Creata 1.7.15:")
    print("   - 访问: https://apkpure.net/mini-world-creata/com.playmini.miniworld")
    print("   - 选择版本 1.7.15")
    print("   - 下载APK并保存为: miniworld_en_1.7.15.apk")
    print()
    print("3. Minecraft Bedrock 1.20.60:")
    print("   - 从Google Play Store购买并下载")
    print("   - 或使用已购买的账号提取APK")
    print("   - 保存为: minecraft_bedrock_1.20.60.apk")

if __name__ == "__main__":
    main()
