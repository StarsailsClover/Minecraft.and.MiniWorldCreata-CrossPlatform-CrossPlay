# 🚀 文档系统快速开始

## 立即体验

### 1. 查看文档站
```
双击打开: docs/index.html
```

### 2. 使用编辑器
```
双击打开: docs/editor/index.html
```

### 3. 从介绍站访问
```
打开: Introducing/index.html
点击导航栏的"文档"链接
```

## 📝 添加第一篇文档

### 使用编辑器（推荐）

1. **打开编辑器**
   - 访问 `docs/editor/index.html`

2. **编写内容**
   ```markdown
   # 我的第一篇文档
   
   这是文档内容...
   ```

3. **填写配置**
   - 点击右侧"配置"按钮
   - 填写作者、描述、标签等

4. **下载文件**
   - 点击"下载 Markdown"
   - 点击"下载配置"

5. **保存文件**
   - 将 `.md` 文件保存到 `docs/posts/guide/my-first-doc.md`
   - 将 `.json` 文件保存到 `docs/posts/guide/my-first-doc.json`

6. **更新导航**
   - 编辑 `docs/script.js`
   - 在 `docsConfig` 中添加：
   ```javascript
   {
       title: '用户指南',
       items: [
           { title: '我的第一篇文档', path: 'guide/my-first-doc' }
       ]
   }
   ```

7. **查看效果**
   - 刷新 `docs/index.html`
   - 在侧边栏找到新文档

## 🎨 自定义主题

### 修改颜色

编辑 `docs/styles.css`:
```css
:root {
    --color-primary: #0071e3;  /* 改成你喜欢的颜色 */
}
```

### 修改字体

编辑 `docs/styles.css`:
```css
body {
    font-family: "你的字体", sans-serif;
}
```

## 🔍 使用搜索

1. 点击顶部搜索框
2. 或按 `Ctrl+K`
3. 输入关键词
4. 点击结果跳转

## ⌨️ 编辑器快捷键

- `Ctrl+B` - 粗体
- `Ctrl+I` - 斜体
- `Ctrl+K` - 插入链接
- `Tab` - 缩进

## 📸 添加图片

1. 将图片放到 `docs/assets/images/`
2. 在 Markdown 中引用：
   ```markdown
   ![图片描述](../assets/images/example.png)
   ```

## 🌐 部署到线上

### GitHub Pages

1. 推送代码到 GitHub
2. 启用 Pages
3. 访问 `https://yourusername.github.io/LightSearch/docs/`

### 本地服务器

```bash
cd docs
python -m http.server 8000
# 访问 http://localhost:8000
```

## ❓ 常见问题

### Q: 文档不显示？
**A**: 检查文件路径和 `script.js` 配置是否正确

### Q: 代码高亮不工作？
**A**: 确保 CDN 链接正常，或下载到本地

### Q: 搜索找不到文档？
**A**: 搜索只匹配标题和分类，确保配置正确

### Q: 编辑器草稿丢失？
**A**: 草稿保存在浏览器本地，清除缓存会丢失

## 📚 更多帮助

查看完整文档：
- [README.md](README.md) - 详细使用说明
- [COMPLETION-REPORT.md](COMPLETION-REPORT.md) - 功能清单

## 🎉 开始创作

现在你可以开始编写文档了！祝你使用愉快！

---

**Made with ❤️ by Sails**
