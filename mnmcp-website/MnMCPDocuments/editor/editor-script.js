// ==================== 初始化 ====================
const editor = document.getElementById('markdownEditor');
const preview = document.getElementById('previewContent');
const docTitle = document.getElementById('docTitle');

// 配置 marked
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true
});

// ==================== 实时预览 ====================
let updateTimeout;
editor.addEventListener('input', () => {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(updatePreview, 300);
});

function updatePreview() {
    const markdown = editor.value;
    const html = marked.parse(markdown);
    preview.innerHTML = html;
    
    // 代码高亮
    preview.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

// ==================== 工具栏操作 ====================
document.querySelectorAll('.toolbar-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        handleToolbarAction(action);
    });
});

function handleToolbarAction(action) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selectedText = editor.value.substring(start, end);
    const beforeText = editor.value.substring(0, start);
    const afterText = editor.value.substring(end);
    
    let newText = '';
    let cursorOffset = 0;
    
    switch(action) {
        case 'bold':
            newText = `**${selectedText || '粗体文字'}**`;
            cursorOffset = selectedText ? newText.length : 2;
            break;
        case 'italic':
            newText = `*${selectedText || '斜体文字'}*`;
            cursorOffset = selectedText ? newText.length : 1;
            break;
        case 'strikethrough':
            newText = `~~${selectedText || '删除线文字'}~~`;
            cursorOffset = selectedText ? newText.length : 2;
            break;
        case 'h1':
            newText = `# ${selectedText || '一级标题'}`;
            cursorOffset = newText.length;
            break;
        case 'h2':
            newText = `## ${selectedText || '二级标题'}`;
            cursorOffset = newText.length;
            break;
        case 'h3':
            newText = `### ${selectedText || '三级标题'}`;
            cursorOffset = newText.length;
            break;
        case 'quote':
            newText = `> ${selectedText || '引用文字'}`;
            cursorOffset = newText.length;
            break;
        case 'code':
            newText = `\`${selectedText || '代码'}\``;
            cursorOffset = selectedText ? newText.length : 1;
            break;
        case 'codeblock':
            newText = `\`\`\`javascript\n${selectedText || '// 代码块'}\n\`\`\``;
            cursorOffset = selectedText ? newText.length : 14;
            break;
        case 'ul':
            newText = `- ${selectedText || '列表项'}`;
            cursorOffset = newText.length;
            break;
        case 'ol':
            newText = `1. ${selectedText || '列表项'}`;
            cursorOffset = newText.length;
            break;
        case 'table':
            newText = `| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 单元格 | 单元格 | 单元格 |`;
            cursorOffset = newText.length;
            break;
        case 'link':
            const url = prompt('请输入链接地址:', 'https://');
            if (url) {
                newText = `[${selectedText || '链接文字'}](${url})`;
                cursorOffset = newText.length;
            }
            break;
        case 'image':
            const imgUrl = prompt('请输入图片地址:', 'https://');
            if (imgUrl) {
                newText = `![${selectedText || '图片描述'}](${imgUrl})`;
                cursorOffset = newText.length;
            }
            break;
        default:
            return;
    }
    
    editor.value = beforeText + newText + afterText;
    editor.focus();
    editor.setSelectionRange(start + cursorOffset, start + cursorOffset);
    updatePreview();
}

// ==================== 键盘快捷键 ====================
editor.addEventListener('keydown', (e) => {
    // Ctrl+B: 粗体
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        handleToolbarAction('bold');
    }
    
    // Ctrl+I: 斜体
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
        e.preventDefault();
        handleToolbarAction('italic');
    }
    
    // Ctrl+K: 链接
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        handleToolbarAction('link');
    }
    
    // Tab: 缩进
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 2;
    }
});

// ==================== 预览切换 ====================
const previewToggle = document.getElementById('previewToggle');
const previewPane = document.getElementById('previewPane');
const editorPane = document.getElementById('editorPane');

previewToggle.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
        previewPane.classList.toggle('active');
        editorPane.style.display = previewPane.classList.contains('active') ? 'none' : 'block';
    }
});

// ==================== 下载功能 ====================
document.getElementById('downloadMd').addEventListener('click', () => {
    const content = editor.value;
    const filename = docTitle.value || '未命名文档';
    downloadFile(content, `${filename}.md`, 'text/markdown');
});

document.getElementById('downloadJson').addEventListener('click', () => {
    const config = {
        title: docTitle.value || '未命名文档',
        description: document.getElementById('configDescription').value,
        author: document.getElementById('configAuthor').value,
        date: new Date().toISOString().split('T')[0],
        tags: document.getElementById('configTags').value.split(',').map(t => t.trim()).filter(t => t),
        category: document.getElementById('configCategory').value
    };
    const content = JSON.stringify(config, null, 2);
    const filename = docTitle.value || '未命名文档';
    downloadFile(content, `${filename}.json`, 'application/json');
});

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// ==================== 保存功能 ====================
document.getElementById('saveDoc').addEventListener('click', () => {
    const data = {
        title: docTitle.value,
        content: editor.value,
        config: {
            description: document.getElementById('configDescription').value,
            author: document.getElementById('configAuthor').value,
            tags: document.getElementById('configTags').value,
            category: document.getElementById('configCategory').value
        }
    };
    
    localStorage.setItem('lightsearch-doc-draft', JSON.stringify(data));
    showNotification('草稿已保存');
});

// ==================== 加载草稿 ====================
function loadDraft() {
    const draft = localStorage.getItem('lightsearch-doc-draft');
    if (draft) {
        try {
            const data = JSON.parse(draft);
            docTitle.value = data.title || '';
            editor.value = data.content || '';
            if (data.config) {
                document.getElementById('configDescription').value = data.config.description || '';
                document.getElementById('configAuthor').value = data.config.author || '';
                document.getElementById('configTags').value = data.config.tags || '';
                document.getElementById('configCategory').value = data.config.category || 'getting-started';
            }
            updatePreview();
        } catch (e) {
            console.error('加载草稿失败:', e);
        }
    }
}

// ==================== 配置面板 ====================
const configToggle = document.getElementById('configToggle');
const configPanel = document.getElementById('configPanel');

configToggle.addEventListener('click', () => {
    configPanel.classList.toggle('active');
});

// ==================== 通知 ====================
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background-color: #0071e3;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// ==================== 自动保存 ====================
setInterval(() => {
    if (editor.value.trim()) {
        const data = {
            title: docTitle.value,
            content: editor.value,
            config: {
                description: document.getElementById('configDescription').value,
                author: document.getElementById('configAuthor').value,
                tags: document.getElementById('configTags').value,
                category: document.getElementById('configCategory').value
            }
        };
        localStorage.setItem('lightsearch-doc-draft', JSON.stringify(data));
    }
}, 30000); // 每30秒自动保存

// ==================== 初始化加载 ====================
window.addEventListener('load', () => {
    loadDraft();
});

// ==================== 添加动画样式 ====================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
