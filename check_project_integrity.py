#!/usr/bin/env python3
"""
项目完整性检查工具
Phase 5 - 开发前检查

检查内容:
1. 核心文件存在性
2. 模块可导入性
3. 配置文件有效性
4. 数据文件完整性
5. 测试可运行性
"""

import sys
import os
import json
import importlib
from pathlib import Path
from typing import List, Tuple, Dict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class IntegrityChecker:
    """完整性检查器"""
    
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
        print(" MnMCP 项目完整性检查")
        print(" Phase 5 - 开发前验证")
        print("=" * 70)
        print(f"{Colors.ENDC}")
        
        # 1. 核心文件检查
        self._check_core_files()
        
        # 2. 模块导入检查
        self._check_module_imports()
        
        # 3. 配置文件检查
        self._check_config_files()
        
        # 4. 数据文件检查
        self._check_data_files()
        
        # 5. 测试文件检查
        self._check_test_files()
        
        # 6. 依赖检查
        self._check_dependencies()
        
        # 打印结果
        self._print_results()
        
        return self.failed == 0
    
    def _check_core_files(self):
        """检查核心文件"""
        print(f"\n{Colors.OKBLUE}[1/6] 检查核心文件...{Colors.ENDC}")
        
        core_files = [
            ("启动脚本", "start.py"),
            ("配置文件", "config.yaml"),
            ("依赖文件", "requirements.txt"),
            ("项目说明", "README.md"),
        ]
        
        for name, file_path in core_files:
            full_path = PROJECT_ROOT / file_path
            exists = full_path.exists()
            self.check(
                f"核心文件: {name}",
                exists,
                f"{file_path} {'存在' if exists else '缺失'}"
            )
    
    def _check_module_imports(self):
        """检查模块导入"""
        print(f"\n{Colors.OKBLUE}[2/6] 检查模块导入...{Colors.ENDC}")
        
        # 添加src到路径
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        
        modules = [
            ("加密模块", "crypto.aes_crypto"),
            ("密码哈希", "crypto.password_hasher"),
            ("方块映射", "protocol.block_mapper"),
            ("协议翻译", "protocol.packet_translator"),
            ("MC协议", "protocol.mc_protocol"),
            ("MNW登录", "protocol.mnw_login"),
            ("代理服务器", "core.proxy_server_v2"),
            ("配置加载", "utils.config_loader"),
        ]
        
        for name, module_path in modules:
            try:
                module = importlib.import_module(module_path)
                self.check(
                    f"模块导入: {name}",
                    True,
                    f"{module_path} 导入成功"
                )
            except Exception as e:
                self.check(
                    f"模块导入: {name}",
                    False,
                    f"{module_path} 导入失败: {e}"
                )
    
    def _check_config_files(self):
        """检查配置文件"""
        print(f"\n{Colors.OKBLUE}[3/6] 检查配置文件...{Colors.ENDC}")
        
        config_file = PROJECT_ROOT / "config.yaml"
        
        if not config_file.exists():
            self.check("配置文件存在", False, "config.yaml 不存在")
            return
        
        self.check("配置文件存在", True)
        
        # 尝试解析YAML
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
            self.check("YAML解析", False, "缺少pyyaml库", warning=True)
        except Exception as e:
            self.check("YAML解析", False, f"解析失败: {e}")
    
    def _check_data_files(self):
        """检查数据文件"""
        print(f"\n{Colors.OKBLUE}[4/6] 检查数据文件...{Colors.ENDC}")
        
        data_files = [
            ("方块映射", "data/mnw_block_mapping_from_go.json", False),
            ("方块映射(备用)", "data/block_mappings.json", True),
        ]
        
        for name, file_path, optional in data_files:
            full_path = PROJECT_ROOT / file_path
            exists = full_path.exists()
            
            if optional and not exists:
                self.check(
                    f"数据文件: {name}",
                    False,
                    f"{file_path} 不存在(可选)",
                    warning=True
                )
            else:
                self.check(
                    f"数据文件: {name}",
                    exists,
                    f"{file_path} {'存在' if exists else '缺失'}"
                )
            
            # 检查JSON有效性
            if exists:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'mappings' in data:
                        count = len(data['mappings'])
                        self.check(
                            f"数据文件内容: {name}",
                            count > 0,
                            f"包含 {count} 个映射"
                        )
                except Exception as e:
                    self.check(
                        f"数据文件内容: {name}",
                        False,
                        f"JSON解析失败: {e}"
                    )
    
    def _check_test_files(self):
        """检查测试文件"""
        print(f"\n{Colors.OKBLUE}[5/6] 检查测试文件...{Colors.ENDC}")
        
        test_files = [
            ("加密测试", "tests/test_crypto.py"),
            ("映射测试", "tests/test_block_mapper.py"),
            ("协议测试", "tests/test_protocol.py"),
        ]
        
        for name, file_path in test_files:
            full_path = PROJECT_ROOT / file_path
            exists = full_path.exists()
            self.check(
                f"测试文件: {name}",
                exists,
                f"{file_path} {'存在' if exists else '缺失'}"
            )
            
            # 检查语法
            if exists:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    compile(code, full_path, 'exec')
                    self.check(
                        f"测试语法: {name}",
                        True,
                        "语法正确"
                    )
                except SyntaxError as e:
                    self.check(
                        f"测试语法: {name}",
                        False,
                        f"语法错误: {e}"
                    )
    
    def _check_dependencies(self):
        """检查依赖"""
        print(f"\n{Colors.OKBLUE}[6/6] 检查依赖...{Colors.ENDC}")
        
        required_deps = [
            ("cryptography", "加密支持", True),
            ("websockets", "WebSocket支持", False),
            ("pyyaml", "YAML解析", False),
        ]
        
        for dep_name, purpose, optional in required_deps:
            try:
                module = importlib.import_module(dep_name)
                version = getattr(module, '__version__', 'unknown')
                self.check(
                    f"依赖: {dep_name}",
                    True,
                    f"已安装 (v{version})"
                )
            except ImportError:
                if optional:
                    self.check(
                        f"依赖: {dep_name}",
                        False,
                        f"未安装 ({purpose}) - 可选",
                        warning=True
                    )
                else:
                    self.check(
                        f"依赖: {dep_name}",
                        False,
                        f"未安装 ({purpose}) - 必需"
                    )
    
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
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ 项目完整性检查通过！{Colors.ENDC}")
            if self.warnings > 0:
                print(f"{Colors.WARNING}⚠️ 有 {self.warnings} 个警告，建议处理{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ 项目完整性检查失败！{Colors.ENDC}")
            print(f"{Colors.FAIL}请修复上述问题后再继续开发{Colors.ENDC}")


def main():
    """主函数"""
    checker = IntegrityChecker()
    success = checker.run_all_checks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
