#!/bin/bash

# MnMCP Git 初始化脚本
# 版本: 26w14a_dev_26.1.1

echo "Initializing MnMCP Git Repository..."

# 初始化 Git 仓库
git init

# 创建分支
git checkout -b main
git checkout -b dev

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: 26w14a_dev_26.1.1 - Phase 1 framework"

# 创建标签
git tag -a "26w14a_dev_26.1.1" -m "Phase 1: Basic framework"

echo "Git repository initialized!"
echo "Current branch: $(git branch --show-current)"
echo "Tags: $(git tag)"
