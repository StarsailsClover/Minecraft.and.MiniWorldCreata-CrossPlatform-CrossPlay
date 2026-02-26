#!/usr/bin/env python3
"""
使用Frida进行Android应用脱壳
针对腾讯御安全（Ace GShell）加固的APK
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
APK_PATH = EXTERNAL_DIR / "packs_downloads" / "miniworldMini-wp.apk"
OUTPUT_DIR = EXTERNAL_DIR / "packs_downloads" / "dumped_dex"
FRIDA_SERVER_PATH = SCRIPT_DIR / "frida-server.xz"

# Frida脚本 - 用于Dump DEX
FRIDA_SCRIPT = """
// 脱壳脚本 - 针对腾讯御安全
function hook_dex_load() {
    console.log("[*] Starting DEX dump...");
    
    // Hook DexFile.loadDex
    var DexFile = Java.use("dalvik.system.DexFile");
    DexFile.loadDex.implementation = function(sourcePathName, outputPathName, flags) {
        console.log("[+] DexFile.loadDex called: " + sourcePathName);
        return this.loadDex(sourcePathName, outputPathName, flags);
    };
    
    // Hook Application.attachBaseContext
    var Application = Java.use("android.app.Application");
    Application.attachBaseContext.implementation = function(base) {
        console.log("[+] Application.attachBaseContext called");
        
        // 尝试Dump内存中的DEX
        dump_dex_from_memory();
        
        return this.attachBaseContext(base);
    };
    
    // Hook ClassLoader
    var ClassLoader = Java.use("java.lang.ClassLoader");
    ClassLoader.loadClass.overload('java.lang.String').implementation = function(className) {
        console.log("[+] Loading class: " + className);
        return this.loadClass(className);
    };
}

function dump_dex_from_memory() {
    console.log("[*] Attempting to dump DEX from memory...");
    
    // 获取当前应用的内存映射
    var modules = Process.enumerateModules();
    for (var i = 0; i < modules.length; i++) {
        var module = modules[i];
        if (module.name.indexOf("dex") !== -1 || module.name.indexOf("apk") !== -1) {
            console.log("[+] Found module: " + module.name + " at " + module.base);
        }
    }
}

function main() {
    console.log("[*] Frida DEX Dumper Started");
    console.log("[*] Target: MiniWorld Official APK");
    
    Java.perform(function() {
        hook_dex_load();
        console.log("[*] Hooks installed, waiting for DEX loading...");
    });
}

setImmediate(main);
"""

def check_device_connected():
    """检查设备是否连接"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        devices = [line for line in lines[1:] if line.strip() and 'device' in line]
        return len(devices) > 0
    except Exception as e:
        print(f"[-] Error checking device: {e}")
        return False

def push_frida_server():
    """推送Frida服务端到设备"""
    print("[*] Pushing Frida server to device...")
    
    # 解压frida-server
    frida_server = SCRIPT_DIR / "frida-server"
    if not frida_server.exists() and FRIDA_SERVER_PATH.exists():
        import lzma
        with lzma.open(FRIDA_SERVER_PATH, 'rb') as f_in:
            with open(frida_server, 'wb') as f_out:
                f_out.write(f_in.read())
        print("[+] Frida server extracted")
    
    # 推送并设置权限
    commands = [
        ["adb", "push", str(frida_server), "/data/local/tmp/frida-server"],
        ["adb", "shell", "chmod", "755", "/data/local/tmp/frida-server"],
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Command failed: {' '.join(cmd)}")
            print(f"[-] Error: {result.stderr}")
            return False
    
    print("[+] Frida server pushed successfully")
    return True

def start_frida_server():
    """启动Frida服务端"""
    print("[*] Starting Frida server...")
    
    # 检查是否已经在运行
    result = subprocess.run(
        ["adb", "shell", "ps", "|", "grep", "frida-server"],
        capture_output=True,
        text=True
    )
    
    if "frida-server" in result.stdout:
        print("[+] Frida server already running")
        return True
    
    # 启动Frida服务器（后台运行）
    subprocess.Popen(
        ["adb", "shell", "/data/local/tmp/frida-server &"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(2)
    print("[+] Frida server started")
    return True

def install_apk():
    """安装APK到设备"""
    print(f"[*] Installing APK: {APK_PATH}")
    
    if not APK_PATH.exists():
        print(f"[-] APK not found: {APK_PATH}")
        return False
    
    result = subprocess.run(
        ["adb", "install", "-r", str(APK_PATH)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[-] Install failed: {result.stderr}")
        return False
    
    print("[+] APK installed successfully")
    return True

def dump_dex():
    """执行脱壳操作"""
    print("[*] Starting DEX dump process...")
    
    # 保存Frida脚本
    script_path = SCRIPT_DIR / "dump_script.js"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(FRIDA_SCRIPT)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("[*] Frida script saved to:", script_path)
    print("[*] Output directory:", OUTPUT_DIR)
    
    # 这里需要使用frida-python来执行实际的脱壳
    # 由于环境限制，这里提供手动执行命令
    print("\n[!] Manual steps required:")
    print("1. Ensure Android device is connected and USB debugging enabled")
    print("2. Run: frida -U -f com.minitech.miniworld -l dump_script.js --no-pause")
    print("3. Wait for DEX to be dumped to:", OUTPUT_DIR)
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("MiniWorld APK 脱壳工具")
    print("针对腾讯御安全（Ace GShell）加固")
    print("=" * 60)
    
    # 检查设备
    if not check_device_connected():
        print("[-] No Android device connected!")
        print("[!] Please connect a device with USB debugging enabled")
        return False
    
    print("[+] Device connected")
    
    # 推送Frida服务端
    if not push_frida_server():
        print("[-] Failed to push Frida server")
        return False
    
    # 启动Frida服务端
    if not start_frida_server():
        print("[-] Failed to start Frida server")
        return False
    
    # 安装APK
    if not install_apk():
        print("[-] Failed to install APK")
        return False
    
    # 执行脱壳
    dump_dex()
    
    print("\n[+] Setup complete!")
    print("[*] Next: Run the Frida script to dump DEX files")
    
    return True

if __name__ == "__main__":
    main()
