#!/usr/bin/env python3
"""
部署验证脚本 - Phase 6
验证项目是否可以在干净环境部署
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class DeployChecker:
    """部署检查器"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results: List[Tuple[str, str, str]] = []
        
    def check(self, name: str, condition: bool, details: str = "", warning: bool = False):
        """记录检查结果"""
        if condition:
            status = "✅ PASS"
            self.passed += 1
        elif warning:
            status = "⚠️ WARN"
            self.warnings += 1
        else:
            status = "❌ FAIL"
            self.failed += 1
        
        self.results.append((name, status, details))
        return condition
    
    def run_all_checks(self):
        """运行所有检查"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("=" * 70)
        print(" MnMCP 部署验证")
        print(" Phase 6 - 部署检查")
        print("=" * 70)
        print(f"{Colors.ENDC}")
        
        # 1. 环境检查
        self._check_environment()
        
        # 2. 文件完整性检查
        self._check_file_integrity()
        
        # 3. 依赖检查
        self._check_dependencies()
        
        # 4. 配置检查
        self._check_configuration()
        
        # 5. 测试运行检查
        self._check_tests()
        
        # 打印结果
        self._print_results()
        
        return self.failed == 0
    
    def _check_environment(self):
        """检查环境"""
        print(f"\n{Colors.OKBLUE}[1/5] 检查环境...{Colors.ENDC}")
        
        # Python版本
        version = sys.version_info
        version_ok = version.major >= 3 and version.minor >= 11
        self.check(
            "Python版本",
            version_ok,
            f"{version.major}.{version.minor}.{version.micro}",
            warning=not version_ok
        )
        
        # pip可用性
        import shutil
        pip_ok = shutil.which("pip") is not None
        self.check(
            "pip可用性",
            pip_ok,
            "可用" if pip_ok else "不可用"
        )
        
        # 磁盘空间
        try:
            total, used, free = shutil.disk_usage(".")
            free_gb = free / (1024**3)
            space_ok = free_gb > 1.0  # 至少1GB
            self.check(
                "磁盘空间",
                space_ok,
                f"{free_gb:.2f} GB 可用",
                warning=not space_ok
            )
        except Exception as e:
            self.check("磁盘空间", False, f"检查失败: {e}")
    
    def _check_file_integrity(self):
        """检查文件完整性"""
        print(f"\n{Colors.OKBLUE}[2/5] 检查文件完整性...{Colors.ENDC}")
        
        required_files = [
            ("启动脚本", "start.py"),
            ("配置文件", "config.yaml"),
            ("依赖文件", "requirements.txt"),
            ("项目说明", "README.md"),
            ("项目状态", "PROJECT_STATUS.md"),
        ]
        
        for name, file_path in required_files:
            exists = Path(file_path).exists()
            self.check(
                f"必需文件: {name}",
                exists,
                f"{file_path} {'存在' if exists else '缺失'}"
            )
        
        # 检查核心目录
        required_dirs = [
            ("源代码", "src"),
            ("测试", "tests"),
            ("数据", "data"),
            ("文档", "docs"),
        ]
        
        for name, dir_path in required_dirs:
            exists = Path(dir_path).exists() and Path(dir_path).is_dir()
            self.check(
                f"必需目录: {name}",
                exists,
                f"{dir_path}/ {'存在' if exists else '缺失'}"
            )
    
    def _check_dependencies(self):
        """检查依赖"""
        print(f"\n{Colors.OKBLUE}[3/5] 检查依赖...{Colors.ENDC}")
        
        # 核心依赖
        core_deps = [
            ("websockets", "WebSocket支持", True),
            ("pyyaml", "YAML解析", True),
        ]
        
        for dep_name, purpose, required in core_deps:
            try:
                __import__(dep_name)
                self.check(
                    f"依赖: {dep_name}",
                    True,
                    f"已安装 ({purpose})"
                )
            except ImportError:
                self.check(
                    f"依赖: {dep_name}",
                    False,
                    f"未安装 ({purpose}) - {'必需' if required else '可选'}",
                    warning=not required
                )
        
        # 可选依赖
        optional_deps = [
            ("cryptography", "生产级加密"),
        ]
        
        for dep_name, purpose in optional_deps:
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', 'unknown')
                self.check(
                    f"可选依赖: {dep_name}",
                    True,
                    f"已安装 v{version} ({purpose})"
                )
            except ImportError:
                self.check(
                    f"可选依赖: {dep_name}",
                    False,
                    f"未安装 ({purpose}) - 将使用简化版",
                    warning=True
                )
    
    def _check_configuration(self):
        """检查配置"""
        print(f"\n{Colors.OKBLUE}[4/5] 检查配置...{Colors.ENDC}")
        
        config_file = Path("config.yaml")
        
        if not config_file.exists():
            self.check("配置文件", False, "config.yaml 不存在")
            return
        
        self.check("配置文件存在", True)
        
        # 尝试解析
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查关键配置项
            required_keys = ['server', 'auth', 'mapping', 'features', 'logging']
            for key in required_keys:
                has_key = key in config
                self.check(
                    f"配置项: {key}",
                    has_key,
                    f"{'存在' if has_key else '缺失'}"
                )
                
        except ImportError:
            self.check("YAML解析", False, "缺少pyyaml库，将使用默认配置", warning=True)
        except Exception as e:
            self.check("YAML解析", False, f"解析失败: {e}")
    
    def _check_tests(self):
        """检查测试"""
        print(f"\n{Colors.OKBLUE}[5/5] 检查测试...{Colors.ENDC}")
        
        # 检查测试文件
        test_files = [
            ("加密测试", "tests/test_crypto.py"),
            ("映射测试", "tests/test_block_mapper.py"),
            ("协议测试", "tests/test_protocol.py"),
        ]
        
        for name, file_path in test_files:
            exists = Path(file_path).exists()
            self.check(
                f"测试文件: {name}",
                exists,
                f"{file_path} {'存在' if exists else '缺失'}"
            )
        
        # 尝试运行测试
        try:
            result = subprocess.run(
                [sys.executable, "tests/test_crypto.py"],
                capture_output=True,
                timeout=30
            )
            test_ok = result.returncode == 0
            self.check(
                "测试运行: 加密模块",
                test_ok,
                "通过" if test_ok else "失败",
                warning=not test_ok
            )
        except Exception as e:
            self.check("测试运行: 加密模块", False, f"运行失败: {e}", warning=True)
    
    def _print_results(self):
        """打印结果"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("=" * 70)
        print(" 检查结果")
        print("=" * 70)
        print(f"{Colors.ENDC}")
        
        for name, status, details in self.results:
            color = Colors.OKGREEN if "PASS" in status else (Colors.WARNING if "WARN" in status else Colors.FAIL)
            print(f"  [{color}{status}{Colors.ENDC}] {name}")
            if details:
                print(f"       {details}")
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("=" * 70)
        print(f" 统计: {Colors.OKGREEN}{self.passed} 通过{Colors.ENDC} | "
              f"{Colors.WARNING}{self.warnings} 警告{Colors.ENDC} | "
              f"{Colors.FAIL}{self.failed} 失败{Colors.ENDC}")
        print("=" * 70)
        print(f"{Colors.ENDC}")
        
        if self.failed == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ 部署验证通过！{Colors.ENDC}")
            if self.warnings > 0:
                print(f"{Colors.WARNING}⚠️ 有 {self.warnings} 个警告，建议处理后再部署{Colors.ENDC}")
            print(f"\n{Colors.OKGREEN}可以运行: python start.py{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ 部署验证失败！{Colors.ENDC}")
            print(f"{Colors.FAIL}请修复上述问题后再部署{Colors.ENDC}")
            print(f"\n{Colors.OKBLUE}安装缺失依赖:{Colors.ENDC}")
            print(f"  pip install websockets pyyaml")


def main():
    """主函数"""
    checker = DeployChecker()
    success = checker.run_all_checks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
