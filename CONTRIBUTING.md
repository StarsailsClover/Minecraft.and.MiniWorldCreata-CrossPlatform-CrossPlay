# 贡献指南

感谢你对 MnMCP 项目的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告Bug

如果你发现了Bug，请通过 [GitHub Issues](https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/issues) 报告，并包含以下信息：

- 问题的清晰描述
- 复现步骤
- 预期行为与实际行为
- 环境信息（操作系统、Python版本等）
- 相关的日志输出

### 建议新功能

有新功能建议？请通过 GitHub Issues 提交，并描述：

- 功能的用途
- 预期的行为
- 可能的实现方案（如果你有想法）

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay.git
   cd Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **进行更改**
   - 遵循现有的代码风格
   - 添加必要的注释
   - 更新相关文档

4. **测试你的更改**
   ```bash
   python -m pytest tests/
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   # 或
   git commit -m "fix: 修复某个bug"
   ```

6. **推送到你的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述你的更改
   - 关联相关的Issue
   - 等待审查

## 代码规范

### Python代码风格

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 4 个空格缩进
- 最大行长度 120 字符
- 使用有意义的变量名

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式（不影响代码含义的更改）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加方块放置同步功能

- 实现方块ID映射转换
- 添加坐标系统转换
- 更新协议翻译器

Fixes #123
```

## 开发流程

1. **阅读文档**
   - [BeforeDevelopment.md](BeforeDevelopment.md)
   - [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
   - [docs/TechnicalDocument.md](docs/TechnicalDocument.md)

2. **设置开发环境**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **运行测试**
   ```bash
   python -m pytest
   ```

4. **代码检查**
   ```bash
   flake8 src/
   black --check src/
   ```

## 项目结构

了解项目结构有助于你更好地贡献：

```
├── src/              # 源代码
├── docs/             # 文档
├── tests/            # 测试
├── tools/            # 工具脚本
└── .github/          # GitHub配置
```

## 获取帮助

如果你需要帮助：

1. 查看 [文档](docs/)
2. 搜索 [Issues](https://github.com/yourusername/Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/issues)
3. 创建新的 Issue 询问

## 行为准则

- 尊重所有参与者
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 许可证

通过贡献你的代码，你同意你的贡献将在 [MIT 许可证](LICENSE) 下发布。