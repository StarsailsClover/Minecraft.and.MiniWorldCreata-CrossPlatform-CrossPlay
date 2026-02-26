#!/usr/bin/env python3
"""创建Release包"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
RELEASE_DIR = PROJECT_DIR / "releases"

def create_release():
    """创建发布包"""
    version = "1.0.0"
    release_name = f"mnmcp-v{version}"
    release_path = RELEASE_DIR / release_name
    
    print(f"[*] 创建发布包: {release_name}")
    
    # 创建发布目录
    if release_path.exists():
        shutil.rmtree(release_path)
    release_path.mkdir(parents=True)
    
    # 复制必要文件
    files_to_include = [
        "src",
        "tests",
        "tools",
        "docs",
        "config",
        "scripts",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
        "LICENSE",
        "requirements.txt",
        "start_proxy.py",
        "test_import.py",
    ]
    
    for item in files_to_include:
        src = PROJECT_DIR / item
        dst = release_path / item
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"  [+] {item}")
    
    # 创建ZIP
    zip_path = RELEASE_DIR / f"{release_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(release_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(release_path)
                zf.write(file_path, arcname)
    
    print(f"[+] 发布包创建完成: {zip_path}")
    print(f"[+] 目录: {release_path}")

if __name__ == "__main__":
    create_release()
