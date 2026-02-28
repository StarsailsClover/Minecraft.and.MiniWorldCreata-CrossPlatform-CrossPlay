#!/usr/bin/env python3
"""
文档脱敏工具
自动识别并脱敏敏感信息
"""

import re
import sys
from pathlib import Path
from datetime import datetime

# 敏感信息模式
SENSITIVE_PATTERNS = [
    # IP地址:端口
    (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b', 'IP:PORT'),
    # 域名:端口
    (r'[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-z]{2,}:[0-9]{2,5}', 'DOMAIN:PORT'),
    # API端点含参数
    (r'/[a-zA-Z0-9/_-]+\?[a-zA-Z0-9_=&]+', 'API_ENDPOINT'),
    # JWT Token
    (r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'JWT_TOKEN'),
    # 认证参数
    (r'auth=[a-f0-9]{32}', 'AUTH_PARAM'),
    # UIN
    (r'uin=\d{10}', 'UIN_PARAM'),
    # AppID
    (r'appid=[a-f0-9]{20}', 'APPID_PARAM'),
]

def mask_sensitive_info(text: str) -> str:
    """脱敏敏感信息"""
    result = text
    
    # 处理IP:端口
    def mask_ip_port(match):
        full = match.group(0)
        return f"[数据处理字符:{len(full)}]"
    
    result = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b', mask_ip_port, result)
    
    # 处理域名:端口
    def mask_domain_port(match):
        full = match.group(0)
        return f"[数据处理字符:{len(full)}]"
    
    result = re.sub(r'[a-zA-Z][-a-zA-Z0-9]*\.[a-zA-Z][-a-zA-Z0-9]*\.[a-z]{2,}:[0-9]{2,5}', mask_domain_port, result)
    
    # 处理API端点（含长参数）
    def mask_api_endpoint(match):
        full = match.group(0)
        if len(full) > 30:  # 只处理长的API端点
            return f"/[数据处理字符:{len(full)}]"
        return full
    
    result = re.sub(r'/[a-zA-Z0-9/_-]+\?[a-zA-Z0-9_=&]{50,}', mask_api_endpoint, result)
    
    # 处理JWT Token
    result = re.sub(r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', '[JWT_TOKEN]', result)
    
    # 处理认证参数
    result = re.sub(r'auth=[a-f0-9]{32}', 'auth=[数据处理字符:37]', result)
    
    # 处理UIN
    result = re.sub(r'uin=\d{10}', 'uin=[数据处理字符:14]', result)
    
    return result

def process_file(input_path: Path, output_path: Path = None) -> bool:
    """处理单个文件"""
    if output_path is None:
        output_path = input_path.with_suffix('.sanitized.md')
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 脱敏处理
        sanitized = mask_sensitive_info(content)
        
        # 添加脱敏标记
        header = f"""<!-- 
此文档已脱敏处理
处理时间: {datetime.now().isoformat()}
原始文件: {input_path.name}
-->

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header + sanitized)
        
        print(f"  ✅ {input_path.name} -> {output_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ {input_path.name}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("文档脱敏工具")
    print("=" * 60)
    print()
    
    # 需要脱敏的文件列表
    docs_to_process = [
        "HANDSHAKE_ANALYSIS_REPORT.md",
        "HANDSHAKE_VERIFICATION_COMPLETE.md",
        "ProtocolAnalysisReport.md",
        "SESSION_021_ALL_PROGRESS.md",
        "SESSION_022_PROGRESS.md",
        "SESSION_023_TESTING_COMPLETE.md",
        "AGENT_CHANGES_LOG.md",
    ]
    
    project_dir = Path(r"C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay")
    
    processed = 0
    failed = 0
    
    for doc_name in docs_to_process:
        doc_path = project_dir / doc_name
        if doc_path.exists():
            if process_file(doc_path):
                processed += 1
            else:
                failed += 1
        else:
            print(f"  ⚠️ 文件不存在: {doc_name}")
    
    print()
    print("=" * 60)
    print(f"处理完成: {processed} 成功, {failed} 失败")
    print("=" * 60)

if __name__ == "__main__":
    main()
