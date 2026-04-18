#!/usr/bin/env python3
"""
MnMCP 项目全面审计脚本

目标：识别所有空实现、框架代码、宣称达成但实际不可运行的部分
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set


class CodeAuditor:
    """代码审计器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[Dict] = []
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'empty_functions': 0,
            'todo_comments': 0,
            'pass_statements': 0,
            'not_implemented': 0,
            'mock_implementations': 0,
        }
    
    def audit_file(self, filepath: Path) -> Dict:
        """审计单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            self.stats['total_files'] += 1
            self.stats['total_lines'] += len(lines)
            
            result = {
                'file': str(filepath.relative_to(self.project_root)),
                'lines': len(lines),
                'issues': [],
            }
            
            # 检查 TODO/FIXME
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line:
                    self.stats['todo_comments'] += 1
                    result['issues'].append({
                        'line': i,
                        'type': 'TODO/FIXME',
                        'content': line.strip()[:80]
                    })
                
                if line.strip() == 'pass':
                    self.stats['pass_statements'] += 1
                    result['issues'].append({
                        'line': i,
                        'type': 'PASS_STATEMENT',
                        'content': line.strip()
                    })
                
                if 'NotImplemented' in line or 'not implemented' in line.lower():
                    self.stats['not_implemented'] += 1
                    result['issues'].append({
                        'line': i,
                        'type': 'NOT_IMPLEMENTED',
                        'content': line.strip()[:80]
                    })
                
                if 'mock' in line.lower() and 'crypto' in line.lower():
                    self.stats['mock_implementations'] += 1
                    result['issues'].append({
                        'line': i,
                        'type': 'MOCK_IMPLEMENTATION',
                        'content': line.strip()[:80]
                    })
            
            # 解析 AST 检查空函数
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        self._check_empty_function(node, result)
            except SyntaxError:
                pass
            
            return result
            
        except Exception as e:
            return {'file': str(filepath), 'error': str(e)}
    
    def _check_empty_function(self, node: ast.FunctionDef, result: Dict):
        """检查空函数"""
        # 检查函数体是否只有 pass/docstring
        body = node.body
        if len(body) == 1:
            if isinstance(body[0], ast.Pass):
                self.stats['empty_functions'] += 1
                result['issues'].append({
                    'line': node.lineno,
                    'type': 'EMPTY_FUNCTION',
                    'content': f"def {node.name}(...): pass"
                })
        elif len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            # 只有 docstring
            self.stats['empty_functions'] += 1
            result['issues'].append({
                'line': node.lineno,
                'type': 'EMPTY_FUNCTION',
                'content': f"def {node.name}(...): # only docstring"
            })
    
    def audit_project(self) -> Dict:
        """审计整个项目"""
        python_files = list(self.project_root.rglob('*.py'))
        
        print(f"Scanning {len(python_files)} Python files...")
        
        for filepath in python_files:
            if '.git' in str(filepath):
                continue
            result = self.audit_file(filepath)
            if result.get('issues'):
                self.issues.append(result)
        
        return {
            'stats': self.stats,
            'issues': self.issues,
        }
    
    def generate_report(self) -> str:
        """生成审计报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("MnMCP 项目审计报告")
        lines.append("=" * 80)
        lines.append("")
        
        # 统计
        lines.append("【统计信息】")
        for key, value in self.stats.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
        
        # 问题文件
        lines.append("【问题文件】")
        for issue in self.issues[:50]:  # 只显示前50个
            lines.append(f"\n文件: {issue['file']}")
            for detail in issue['issues'][:10]:  # 每文件最多10个问题
                lines.append(f"  行 {detail['line']}: [{detail['type']}] {detail['content']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """主函数"""
    project_root = r"D:\Coding\BlockConnect\BlockConnect-MnMCP\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay"
    
    auditor = CodeAuditor(project_root)
    result = auditor.audit_project()
    
    report = auditor.generate_report()
    print(report)
    
    # 保存报告
    report_path = Path(project_root) / "AUDIT_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
