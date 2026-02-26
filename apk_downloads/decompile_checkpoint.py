#!/usr/bin/env python3
"""
断点续传式APK反编译脚本
支持进度保存、断点恢复、后台运行
"""

import os
import sys
import json
import time
import shutil
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

# 动态获取路径
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"

# 配置
APK_NAME = "miniworld_cn_1.53.1.apk"
APK_PATH = EXTERNAL_DIR / "apk_downloads" / APK_NAME
OUTPUT_DIR = EXTERNAL_DIR / "apk_downloads" / "miniworld_cn_decompiled"
TOOLS_DIR = PROJECT_DIR / "tools"
APKTOOL_PATH = TOOLS_DIR / "apktool.jar"
JADX_PATH = TOOLS_DIR / "jadx" / "bin" / "jadx.bat"

# 检查点文件
CHECKPOINT_FILE = PROJECT_DIR / "reverse_engineering" / "decompile_checkpoint.json"
LOG_FILE = PROJECT_DIR / "reverse_engineering" / "decompile_log.txt"
PROGRESS_FILE = PROJECT_DIR / "reverse_engineering" / "decompile_progress.json"

class DecompileCheckpoint:
    """反编译检查点管理器"""
    
    def __init__(self):
        self.checkpoint = self.load_checkpoint()
        self.log_file = open(LOG_FILE, 'a', encoding='utf-8')
    
    def load_checkpoint(self):
        """加载检查点"""
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "apk_name": APK_NAME,
            "apk_path": str(APK_PATH),
            "apk_size": APK_PATH.stat().st_size if APK_PATH.exists() else 0,
            "apk_hash": self.get_file_hash(APK_PATH) if APK_PATH.exists() else "",
            "stages": {
                "apktool": {
                    "status": "pending",  # pending, running, completed, failed
                    "started": None,
                    "completed": None,
                    "output_dir": str(OUTPUT_DIR),
                    "retry_count": 0
                },
                "jadx": {
                    "status": "pending",
                    "started": None,
                    "completed": None,
                    "output_dir": str(OUTPUT_DIR / "jadx_sources"),
                    "retry_count": 0
                },
                "analysis": {
                    "status": "pending",
                    "started": None,
                    "completed": None,
                    "results": {}
                }
            },
            "total_time_seconds": 0,
            "errors": []
        }
    
    def save_checkpoint(self):
        """保存检查点"""
        self.checkpoint["updated"] = datetime.now().isoformat()
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.checkpoint, f, indent=2, ensure_ascii=False)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        self.log_file.write(log_line + '\n')
        self.log_file.flush()
    
    def get_file_hash(self, filepath):
        """计算文件哈希"""
        if not filepath.exists():
            return ""
        hash_obj = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def update_stage(self, stage, status, **kwargs):
        """更新阶段状态"""
        if stage in self.checkpoint["stages"]:
            self.checkpoint["stages"][stage]["status"] = status
            for key, value in kwargs.items():
                self.checkpoint["stages"][stage][key] = value
            self.save_checkpoint()
    
    def add_error(self, stage, error_message):
        """添加错误记录"""
        error = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "message": error_message
        }
        self.checkpoint["errors"].append(error)
        self.save_checkpoint()
    
    def close(self):
        """关闭资源"""
        self.log_file.close()

def run_apktool(checkpoint):
    """运行apktool反编译"""
    stage_info = checkpoint.checkpoint["stages"]["apktool"]
    
    # 检查是否已完成
    if stage_info["status"] == "completed":
        checkpoint.log("[apktool] 阶段已完成，跳过")
        return True
    
    # 检查是否需要清理
    if stage_info["status"] == "failed" and stage_info["retry_count"] > 0:
        checkpoint.log(f"[apktool] 重试 {stage_info['retry_count']}")
        if OUTPUT_DIR.exists():
            checkpoint.log(f"[apktool] 清理旧目录: {OUTPUT_DIR}")
            shutil.rmtree(OUTPUT_DIR)
    
    checkpoint.update_stage("apktool", "running", started=datetime.now().isoformat())
    checkpoint.log("="*70)
    checkpoint.log("[阶段1/3] apktool反编译")
    checkpoint.log("="*70)
    
    cmd = [
        "java", "-jar", str(APKTOOL_PATH),
        "d", str(APK_PATH),
        "-o", str(OUTPUT_DIR),
        "-f"
    ]
    
    checkpoint.log(f"命令: {' '.join(cmd[:5])} ...")
    checkpoint.log(f"输出目录: {OUTPUT_DIR}")
    checkpoint.log("预计时间: 5-15分钟\n")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 实时读取输出
        for line in process.stdout:
            line = line.strip()
            if line:
                checkpoint.log(f"  {line}")
        
        process.wait()
        elapsed = time.time() - start_time
        
        if process.returncode == 0:
            checkpoint.log(f"\n[apktool] ✓ 成功 (耗时: {elapsed/60:.1f}分钟)")
            checkpoint.update_stage(
                "apktool",
                "completed",
                completed=datetime.now().isoformat(),
                elapsed_seconds=elapsed
            )
            return True
        else:
            checkpoint.log(f"\n[apktool] ✗ 失败 (返回码: {process.returncode})")
            checkpoint.add_error("apktool", f"返回码: {process.returncode}")
            checkpoint.update_stage(
                "apktool",
                "failed",
                retry_count=stage_info.get("retry_count", 0) + 1
            )
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        checkpoint.log(f"\n[apktool] ✗ 异常: {str(e)}")
        checkpoint.add_error("apktool", str(e))
        checkpoint.update_stage(
            "apktool",
            "failed",
            retry_count=stage_info.get("retry_count", 0) + 1
        )
        return False

def run_jadx(checkpoint):
    """运行jadx反编译"""
    stage_info = checkpoint.checkpoint["stages"]["jadx"]
    sources_dir = OUTPUT_DIR / "jadx_sources"
    
    # 检查是否已完成
    if stage_info["status"] == "completed":
        checkpoint.log("[jadx] 阶段已完成，跳过")
        return True
    
    # 检查apktool是否完成
    if checkpoint.checkpoint["stages"]["apktool"]["status"] != "completed":
        checkpoint.log("[jadx] apktool未完成，跳过jadx")
        return False
    
    checkpoint.update_stage("jadx", "running", started=datetime.now().isoformat())
    checkpoint.log("\n" + "="*70)
    checkpoint.log("[阶段2/3] jadx反编译")
    checkpoint.log("="*70)
    
    # 清理旧目录
    if sources_dir.exists():
        checkpoint.log(f"[jadx] 清理旧目录: {sources_dir}")
        shutil.rmtree(sources_dir)
    
    cmd = [
        str(JADX_PATH),
        "-d", str(sources_dir),
        "--show-bad-code",
        "--no-res",
        str(APK_PATH)
    ]
    
    checkpoint.log(f"命令: jadx -d {sources_dir} ...")
    checkpoint.log(f"源代码目录: {sources_dir}")
    checkpoint.log("预计时间: 10-30分钟\n")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 实时读取输出
        for line in process.stdout:
            line = line.strip()
            if line:
                checkpoint.log(f"  {line}")
        
        process.wait()
        elapsed = time.time() - start_time
        
        # 检查是否生成源代码
        if sources_dir.exists() and len(list(sources_dir.iterdir())) > 0:
            checkpoint.log(f"\n[jadx] ✓ 完成 (耗时: {elapsed/60:.1f}分钟)")
            checkpoint.update_stage(
                "jadx",
                "completed",
                completed=datetime.now().isoformat(),
                elapsed_seconds=elapsed
            )
            return True
        else:
            checkpoint.log(f"\n[jadx] ✗ 未生成源代码")
            checkpoint.add_error("jadx", "未生成源代码")
            checkpoint.update_stage(
                "jadx",
                "failed",
                retry_count=stage_info.get("retry_count", 0) + 1
            )
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        checkpoint.log(f"\n[jadx] ✗ 异常: {str(e)}")
        checkpoint.add_error("jadx", str(e))
        checkpoint.update_stage(
            "jadx",
            "failed",
            retry_count=stage_info.get("retry_count", 0) + 1
        )
        return False

def run_analysis(checkpoint):
    """运行分析阶段"""
    stage_info = checkpoint.checkpoint["stages"]["analysis"]
    
    # 检查是否已完成
    if stage_info["status"] == "completed":
        checkpoint.log("[analysis] 阶段已完成，跳过")
        return True
    
    # 检查前置阶段
    if checkpoint.checkpoint["stages"]["apktool"]["status"] != "completed":
        checkpoint.log("[analysis] apktool未完成，跳过分析")
        return False
    
    checkpoint.update_stage("analysis", "running", started=datetime.now().isoformat())
    checkpoint.log("\n" + "="*70)
    checkpoint.log("[阶段3/3] 分析反编译结果")
    checkpoint.log("="*70)
    
    start_time = time.time()
    results = {}
    
    # 1. 统计文件
    if OUTPUT_DIR.exists():
        total_files = 0
        smali_files = 0
        smali_classes = set()
        
        for root, dirs, files in os.walk(OUTPUT_DIR):
            total_files += len(files)
            if 'smali' in os.path.basename(root):
                smali_files += len(files)
                if 'smali_classes' in root:
                    class_num = root.split('smali_classes')[-1].split(os.sep)[0]
                    if class_num.isdigit():
                        smali_classes.add(int(class_num))
        
        results["file_stats"] = {
            "total_files": total_files,
            "smali_files": smali_files,
            "smali_classes": len(smali_classes) + 1
        }
        
        checkpoint.log(f"总文件数: {total_files}")
        checkpoint.log(f"smali文件数: {smali_files}")
        checkpoint.log(f"smali类别数: {len(smali_classes) + 1}")
    
    # 2. 检查关键目录
    key_items = [
        ("AndroidManifest.xml", "file"),
        ("smali", "dir"),
        ("lib", "dir"),
        ("assets", "dir"),
        ("jadx_sources", "dir"),
    ]
    
    checkpoint.log("\n[关键目录/文件]")
    key_status = {}
    for item, item_type in key_items:
        path = OUTPUT_DIR / item
        if path.exists():
            if item_type == "dir":
                try:
                    count = len(list(path.iterdir()))
                    checkpoint.log(f"  ✓ {item}/ ({count} 项)")
                    key_status[item] = {"exists": True, "count": count}
                except:
                    checkpoint.log(f"  ✓ {item}/")
                    key_status[item] = {"exists": True}
            else:
                size = path.stat().st_size / 1024
                checkpoint.log(f"  ✓ {item} ({size:.1f} KB)")
                key_status[item] = {"exists": True, "size_kb": size}
        else:
            checkpoint.log(f"  ✗ {item}")
            key_status[item] = {"exists": False}
    
    results["key_items"] = key_status
    
    # 3. 搜索协议相关文件
    checkpoint.log("\n[搜索协议相关文件]")
    keywords = [
        ("network", "网络相关"),
        ("socket", "Socket通信"),
        ("tcp", "TCP协议"),
        ("udp", "UDP协议"),
        ("http", "HTTP协议"),
        ("protocol", "协议实现"),
        ("packet", "数据包"),
        ("message", "消息"),
        ("encrypt", "加密"),
        ("decrypt", "解密"),
        ("aes", "AES加密"),
        ("login", "登录"),
        ("auth", "认证"),
    ]
    
    smali_dir = OUTPUT_DIR / "smali"
    keyword_results = {}
    
    if smali_dir.exists():
        for keyword, desc in keywords:
            count = 0
            for root, dirs, files in os.walk(smali_dir):
                for file in files:
                    if keyword.lower() in file.lower():
                        count += 1
            
            if count > 0:
                checkpoint.log(f"  {desc} ({keyword}): {count} 个文件")
                keyword_results[keyword] = {"desc": desc, "count": count}
    
    results["keyword_search"] = keyword_results
    
    # 保存分析结果
    elapsed = time.time() - start_time
    checkpoint.update_stage(
        "analysis",
        "completed",
        completed=datetime.now().isoformat(),
        elapsed_seconds=elapsed,
        results=results
    )
    
    checkpoint.log(f"\n[analysis] ✓ 完成 (耗时: {elapsed:.1f}秒)")
    return True

def print_status(checkpoint):
    """打印当前状态"""
    print("\n" + "="*70)
    print("反编译状态报告")
    print("="*70)
    
    print(f"\nAPK文件: {APK_NAME}")
    print(f"APK大小: {APK_PATH.stat().st_size / 1024 / 1024 / 1024:.2f} GB")
    print(f"检查点: {CHECKPOINT_FILE}")
    print(f"日志文件: {LOG_FILE}")
    
    print("\n[阶段状态]")
    for stage_name, stage_info in checkpoint.checkpoint["stages"].items():
        status = stage_info["status"]
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "❓")
        
        print(f"  {status_icon} {stage_name}: {status}")
        
        if stage_info.get("started"):
            print(f"     开始: {stage_info['started']}")
        if stage_info.get("completed"):
            print(f"     完成: {stage_info['completed']}")
        if stage_info.get("retry_count", 0) > 0:
            print(f"     重试: {stage_info['retry_count']} 次")
    
    if checkpoint.checkpoint["errors"]:
        print(f"\n[错误记录] ({len(checkpoint.checkpoint['errors'])} 个)")
        for error in checkpoint.checkpoint["errors"][-3:]:  # 显示最后3个
            print(f"  [{error['stage']}] {error['message'][:50]}")
    
    print("\n" + "="*70)

def main():
    """主函数"""
    checkpoint = DecompileCheckpoint()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print_status(checkpoint)
            checkpoint.close()
            return
        elif sys.argv[1] == "reset":
            checkpoint.log("[重置] 删除检查点文件")
            if CHECKPOINT_FILE.exists():
                CHECKPOINT_FILE.unlink()
            checkpoint = DecompileCheckpoint()
    
    checkpoint.log("="*70)
    checkpoint.log("断点续传式APK反编译工具")
    checkpoint.log("="*70)
    
    # 检查APK
    if not APK_PATH.exists():
        checkpoint.log(f"✗ APK文件不存在: {APK_PATH}")
        checkpoint.close()
        return
    
    # 检查APK是否变化
    current_hash = checkpoint.get_file_hash(APK_PATH)
    if checkpoint.checkpoint["apk_hash"] and checkpoint.checkpoint["apk_hash"] != current_hash:
        checkpoint.log("⚠ APK文件已变化，重置检查点")
        checkpoint.checkpoint = checkpoint.load_checkpoint()
        checkpoint.checkpoint["apk_hash"] = current_hash
        checkpoint.save_checkpoint()
    
    # 执行各阶段
    start_time = time.time()
    
    # 阶段1: apktool
    if not run_apktool(checkpoint):
        checkpoint.log("\n✗ apktool阶段失败，停止")
        checkpoint.close()
        return
    
    # 阶段2: jadx
    if not run_jadx(checkpoint):
        checkpoint.log("\n⚠ jadx阶段失败，继续分析")
    
    # 阶段3: 分析
    run_analysis(checkpoint)
    
    # 完成
    total_time = time.time() - start_time
    checkpoint.checkpoint["total_time_seconds"] = total_time
    checkpoint.save_checkpoint()
    
    checkpoint.log("\n" + "="*70)
    checkpoint.log("反编译完成")
    checkpoint.log(f"总耗时: {total_time/60:.1f} 分钟")
    checkpoint.log(f"输出目录: {OUTPUT_DIR}")
    checkpoint.log(f"检查点: {CHECKPOINT_FILE}")
    checkpoint.log("="*70)
    
    checkpoint.close()

if __name__ == "__main__":
    main()
