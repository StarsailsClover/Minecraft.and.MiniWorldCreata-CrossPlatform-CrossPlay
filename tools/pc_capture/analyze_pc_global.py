#!/usr/bin/env python3
"""
分析PC外服版并与国服对比
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent
EXTERNAL_DIR = PROJECT_DIR.parent / "MnMCPResources"
CN_PC_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_CN" / "miniworldLauncher"
GLOBAL_PC_DIR = EXTERNAL_DIR / "packs_downloads" / "miniworldPC_Global" / "miniworldOverseasgame"
OUTPUT_DIR = EXTERNAL_DIR / "packs_downloads" / "pc_global_analysis"

def check_directories():
    """检查目录是否存在"""
    print("[*] 检查PC版目录...")
    
    if not CN_PC_DIR.exists():
        print(f"[-] 国服PC目录不存在: {CN_PC_DIR}")
        return False
    
    if not GLOBAL_PC_DIR.exists():
        print(f"[-] 外服PC目录不存在: {GLOBAL_PC_DIR}")
        return False
    
    print(f"[+] 国服PC目录: {CN_PC_DIR}")
    print(f"[+] 外服PC目录: {GLOBAL_PC_DIR}")
    
    return True

def analyze_directory_structure(game_dir, name):
    """分析目录结构"""
    print(f"\n[*] 分析{name}目录结构...")
    
    info = {
        "name": name,
        "total_files": 0,
        "exe_files": [],
        "dll_files": [],
        "config_files": [],
        "log_files": [],
        "size_mb": 0
    }
    
    for root, dirs, files in os.walk(game_dir):
        for file in files:
            file_path = Path(root) / file
            info["total_files"] += 1
            
            # 统计文件大小
            try:
                info["size_mb"] += file_path.stat().st_size
            except:
                pass
            
            # 分类文件
            if file.endswith('.exe'):
                info["exe_files"].append(str(file_path.relative_to(game_dir)))
            elif file.endswith('.dll'):
                info["dll_files"].append(str(file_path.relative_to(game_dir)))
            elif file.endswith(('.json', '.xml', '.ini', '.cfg', '.config')):
                info["config_files"].append(str(file_path.relative_to(game_dir)))
            elif file.endswith('.log'):
                info["log_files"].append(str(file_path.relative_to(game_dir)))
    
    info["size_mb"] = info["size_mb"] / (1024 * 1024)
    
    print(f"  总文件数: {info['total_files']}")
    print(f"  总大小: {info['size_mb']:.2f} MB")
    print(f"  EXE文件: {len(info['exe_files'])}")
    print(f"  DLL文件: {len(info['dll_files'])}")
    print(f"  配置文件: {len(info['config_files'])}")
    print(f"  日志文件: {len(info['log_files'])}")
    
    return info

def analyze_logs(game_dir, name):
    """分析日志文件"""
    print(f"\n[*] 分析{name}日志...")
    
    log_files = list(game_dir.rglob("*.log"))
    findings = {
        "server_urls": [],
        "api_endpoints": [],
        "ip_addresses": [],
        "version_info": []
    }
    
    # 搜索模式
    patterns = {
        "urls": r'https?://[^\s<>"\']+',
        "ips": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "version": r'version[\s:=]+([0-9.]+)',
        "api": r'/api/[a-zA-Z0-9/_]+'
    }
    
    for log_file in log_files[:5]:  # 限制文件数量
        print(f"  [+] 分析: {log_file.name}")
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # 搜索URL
                urls = re.findall(patterns["urls"], content)
                findings["server_urls"].extend(urls[:20])  # 限制数量
                
                # 搜索IP
                ips = re.findall(patterns["ips"], content)
                findings["ip_addresses"].extend(ips[:20])
                
                # 搜索版本
                versions = re.findall(patterns["version"], content, re.IGNORECASE)
                findings["version_info"].extend(versions[:10])
                
                # 搜索API
                apis = re.findall(patterns["api"], content)
                findings["api_endpoints"].extend(apis[:20])
        
        except Exception as e:
            print(f"    [-] 错误: {e}")
    
    # 去重
    for key in findings:
        findings[key] = list(set(findings[key]))
    
    print(f"  发现URL: {len(findings['server_urls'])}")
    print(f"  发现IP: {len(findings['ip_addresses'])}")
    print(f"  发现版本: {len(findings['version_info'])}")
    
    return findings

def compare_versions(cn_info, global_info, cn_logs, global_logs):
    """对比两个版本"""
    print("\n[*] 对比国服/外服差异...")
    
    comparison = {
        "analysis_time": datetime.now().isoformat(),
        "size_diff_mb": global_info["size_mb"] - cn_info["size_mb"],
        "files_diff": global_info["total_files"] - cn_info["total_files"],
        "cn_urls": cn_logs["server_urls"][:10],
        "global_urls": global_logs["server_urls"][:10],
        "cn_version": cn_logs["version_info"][:5],
        "global_version": global_logs["version_info"][:5]
    }
    
    print(f"  大小差异: {comparison['size_diff_mb']:+.2f} MB")
    print(f"  文件数差异: {comparison['files_diff']:+d}")
    
    print("\n  国服服务器URL:")
    for url in comparison["cn_urls"][:5]:
        print(f"    - {url}")
    
    print("\n  外服服务器URL:")
    for url in comparison["global_urls"][:5]:
        print(f"    - {url}")
    
    return comparison

def generate_report(cn_info, global_info, cn_logs, global_logs, comparison):
    """生成分析报告"""
    print("\n[*] 生成分析报告...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = OUTPUT_DIR / "PC_GLOBAL_COMPARISON.md"
    
    report = f"""# PC版国服/外服对比分析报告

## 分析时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 基本信息对比

| 项目 | 国服 | 外服 | 差异 |
|------|------|------|------|
| 总大小 | {cn_info['size_mb']:.2f} MB | {global_info['size_mb']:.2f} MB | {comparison['size_diff_mb']:+.2f} MB |
| 文件数 | {cn_info['total_files']} | {global_info['total_files']} | {comparison['files_diff']:+d} |
| EXE文件 | {len(cn_info['exe_files'])} | {len(global_info['exe_files'])} | {len(global_info['exe_files']) - len(cn_info['exe_files']):+d} |
| DLL文件 | {len(cn_info['dll_files'])} | {len(global_info['dll_files'])} | {len(global_info['dll_files']) - len(cn_info['dll_files']):+d} |

## 服务器地址对比

### 国服服务器
{chr(10).join(['- `' + url + '`' for url in comparison['cn_urls']]) if comparison['cn_urls'] else '- 未找到'}

### 外服服务器
{chr(10).join(['- `' + url + '`' for url in comparison['global_urls']]) if comparison['global_urls'] else '- 未找到'}

## 版本信息

### 国服版本
{chr(10).join(['- ' + v for v in comparison['cn_version']]) if comparison['cn_version'] else '- 未找到'}

### 外服版本
{chr(10).join(['- ' + v for v in comparison['global_version']]) if comparison['global_version'] else '- 未找到'}

## 关键发现

### 服务器域名差异
- **国服**: 使用 `mini1.cn` 域名
- **外服**: 使用 `miniworldgame.com` 或 `playmini.net` 域名

### 登录认证差异
- **国服**: 迷你号/手机号登录
- **外服**: Google/Facebook/Discord OAuth

### 内容差异
- **国服**: 有防沉迷系统、内容审查
- **外服**: 国际版内容，无防沉迷

## 协议分析建议

1. **抓包对比**
   - 同时抓包国服和外服
   - 对比登录流程差异
   - 对比数据包结构

2. **代码对比**
   - 对比EXE/DLL文件差异
   - 查找协议处理代码
   - 识别加密算法差异

3. **服务器分析**
   - 解析外服服务器IP
   - 测试连接端口
   - 分析负载均衡策略

## 文件位置

- 国服PC: `MnMCPResources/packs_downloads/miniworldPC_CN/`
- 外服PC: `MnMCPResources/packs_downloads/miniworldPC_Global/`
- 分析报告: `MnMCPResources/packs_downloads/pc_global_analysis/`

## 下一步行动

1. [ ] 使用Wireshark抓包外服PC版
2. [ ] 对比国服/外服登录协议
3. [ ] 分析数据包加密差异
4. [ ] 测试外服房间联机功能
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[+] 报告保存: {report_file}")
    return report_file

def main():
    """主函数"""
    print("=" * 60)
    print("PC版国服/外服对比分析工具")
    print("=" * 60)
    
    # 检查目录
    if not check_directories():
        return False
    
    # 分析目录结构
    cn_info = analyze_directory_structure(CN_PC_DIR, "国服")
    global_info = analyze_directory_structure(GLOBAL_PC_DIR, "外服")
    
    # 分析日志
    cn_logs = analyze_logs(CN_PC_DIR, "国服")
    global_logs = analyze_logs(GLOBAL_PC_DIR, "外服")
    
    # 对比版本
    comparison = compare_versions(cn_info, global_info, cn_logs, global_logs)
    
    # 生成报告
    report_file = generate_report(cn_info, global_info, cn_logs, global_logs, comparison)
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print("=" * 60)
    print(f"\n分析报告: {report_file}")
    print("\n下一步:")
    print("1. 查看对比报告")
    print("2. 使用Wireshark抓包外服PC版")
    print("3. 对比国服/外服协议差异")
    
    return True

if __name__ == "__main__":
    main()
