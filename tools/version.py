# MnMCP 版本命名工具

import datetime


def get_version(branch: str = "dev", main_commits: int = 1, phase: int = 1) -> str:
    """
    生成版本号
    
    格式: [年份]w[周数]a_[分支名]_[年份].[main分支提交次数].[小版本号]
    
    Args:
        branch: 分支名 (main/dev)
        main_commits: main分支提交次数
        phase: 开发阶段 (1-10)
    
    Returns:
        版本号字符串
    """
    now = datetime.datetime.now()
    year = now.year % 100  # 取后两位
    week = now.isocalendar()[1]  # ISO周数
    
    if branch == "main":
        minor = 0
    else:
        minor = phase
    
    return f"{year}w{week}a_{branch}_{year}.{main_commits}.{minor}"


def get_current_version() -> str:
    """获取当前版本号"""
    return "26w14a_dev_26.1.1"


if __name__ == "__main__":
    # 示例
    print("Current version:", get_current_version())
    print("Next dev version:", get_version("dev", 1, 2))
    print("Next main version:", get_version("main", 2, 0))
