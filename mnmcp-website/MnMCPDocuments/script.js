// ==================== 文档配置 ====================
const docsConfig = {
    sections: [
        {
            title: '快速开始',
            items: [
                { title: '介绍', path: 'getting-started/introduction' },
                { title: '安装', path: 'getting-started/installation' },
                { title: '快速上手', path: 'getting-started/quick-start' }
            ]
        },
        {
            title: '用户指南',
            items: [
                { title: '基础使用', path: 'guide/basic-usage' },
                { title: '搜索引擎配置', path: 'guide/search-engines' },
                { title: '主题设置', path: 'guide/themes' },
                { title: '快捷键', path: 'guide/shortcuts' }
            ]
        },
        {
            title: '高级功能',
            items: [
                { title: '自定义引擎', path: 'advanced/custom-engines' },
                { title: '主题开发', path: 'advanced/theme-development' },
                { title: 'API 文档', path: 'advanced/api' }
            ]
        },
        {
            title: '其他',
            items: [
                { title: '常见问题', path: 'misc/faq' },
                { title: '更新日志', path: 'misc/changelog' },
                { title: '贡献指南', path: 'misc/contributing' }
            ]
        }
    ]
};

// ==================== 全局变量 ====================
let currentDoc = null;
let allDocs = [];

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initSearch();
    initImageModal();
    initKeyboardShortcuts();
    loadDocFromURL();
});

// ==================== 侧边栏 ====================
function initSidebar() {
    const sidebarContent = document.getElementById('sidebarContent');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    // 生成侧边栏菜单
    let html = '';
    docsConfig.sections.forEach(section => {
        html += `
            <div class="sidebar-section">
                <div class="sidebar-section-title">${section.title}</div>
                <ul class="sidebar-menu">
        `;
        section.items.forEach(item => {
            html += `
                <li>
                    <a href="#${item.path}" data-path="${item.path}">
                        ${item.title}
                    </a>
                </li>
            `;
            allDocs.push({ ...item, section: section.title });
        });
        html += `
                </ul>
            </div>
        `;
    });
    sidebarContent.innerHTML = html;
    
    // 绑定点击事件
    sidebarContent.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const path = link.dataset.path;
            loadDoc(path);
            updateActiveLink(link);
            
            // 移动端关闭侧边栏
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });
    
    // 移动端切换
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
}

function updateActiveLink(activeLink) {
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    activeLink.classList.add('active');
}

// ==================== 加载文档 ====================
async function loadDoc(path) {
    try {
        // 尝试加载 JSON 配置
        const configResponse = await fetch(`posts/${path}.json`);
        let config = {};
        if (configResponse.ok) {
            config = await configResponse.json();
        }
        
        // 加载 Markdown 内容
        const mdResponse = await fetch(`posts/${path}.md`);
        if (!mdResponse.ok) {
            throw new Error('文档不存在');
        }
        
        const markdown = await mdResponse.text();
        const html = marked.parse(markdown);
        
        // 渲染文档
        const docContent = document.getElementById('docContent');
        docContent.innerHTML = html;
        
        // 代码高亮
        docContent.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        // 生成目录
        generateTOC();
        
        // 绑定图片点击事件
        bindImageClick();
        
        // 更新 URL
        window.location.hash = path;
        
        // 滚动到顶部
        window.scrollTo(0, 0);
        
        currentDoc = { path, config };
    } catch (error) {
        console.error('加载文档失败:', error);
        showError('文档加载失败，请检查文件是否存在。');
    }
}

function loadDocFromURL() {
    const hash = window.location.hash.slice(1);
    if (hash) {
        loadDoc(hash);
        const link = document.querySelector(`[data-path="${hash}"]`);
        if (link) {
            updateActiveLink(link);
        }
    }
}

function showError(message) {
    const docContent = document.getElementById('docContent');
    docContent.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
            <h2>😕 ${message}</h2>
            <p style="color: var(--color-text-secondary); margin-top: 16px;">
                <a href="#" onclick="location.reload()">返回首页</a>
            </p>
        </div>
    `;
}

// ==================== 目录生成 ====================
function generateTOC() {
    const docContent = document.getElementById('docContent');
    const tocContent = document.getElementById('tocContent');
    const headings = docContent.querySelectorAll('h2, h3');
    
    if (headings.length === 0) {
        tocContent.innerHTML = '<p style="color: var(--color-text-secondary); font-size: 13px;">暂无目录</p>';
        return;
    }
    
    let html = '<ul style="list-style: none; padding-left: 0;">';
    headings.forEach((heading, index) => {
        const id = `heading-${index}`;
        heading.id = id;
        const level = heading.tagName === 'H2' ? 0 : 12;
        html += `
            <li style="padding-left: ${level}px;">
                <a href="#${id}" class="toc-link">${heading.textContent}</a>
            </li>
        `;
    });
    html += '</ul>';
    tocContent.innerHTML = html;
    
    // 绑定点击事件
    tocContent.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // 滚动高亮
    observeTOC(headings);
}

function observeTOC(headings) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                document.querySelectorAll('.toc-link').forEach(link => {
                    link.classList.remove('active');
                });
                const activeLink = document.querySelector(`.toc-link[href="#${id}"]`);
                if (activeLink) {
                    activeLink.classList.add('active');
                }
            }
        });
    }, { rootMargin: '-100px 0px -80% 0px' });
    
    headings.forEach(heading => observer.observe(heading));
}

// ==================== 搜索功能 ====================
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const modalSearchInput = document.getElementById('modalSearchInput');
    const searchModal = document.getElementById('searchModal');
    const searchClose = document.getElementById('searchClose');
    const searchResults = document.getElementById('searchResults');
    
    // 点击搜索框打开模态框
    searchInput.addEventListener('click', () => {
        searchModal.classList.add('active');
        modalSearchInput.focus();
    });
    
    // 关闭模态框
    searchClose.addEventListener('click', () => {
        searchModal.classList.remove('active');
    });
    
    searchModal.addEventListener('click', (e) => {
        if (e.target === searchModal) {
            searchModal.classList.remove('active');
        }
    });
    
    // 搜索
    let searchTimeout;
    modalSearchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(e.target.value);
        }, 300);
    });
    
    function performSearch(query) {
        if (!query.trim()) {
            searchResults.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--color-text-secondary);">输入关键词开始搜索</p>';
            return;
        }
        
        const results = allDocs.filter(doc => 
            doc.title.toLowerCase().includes(query.toLowerCase()) ||
            doc.section.toLowerCase().includes(query.toLowerCase())
        );
        
        if (results.length === 0) {
            searchResults.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--color-text-secondary);">未找到相关文档</p>';
            return;
        }
        
        let html = '';
        results.forEach(result => {
            html += `
                <div class="search-result-item" data-path="${result.path}">
                    <div class="search-result-title">${result.title}</div>
                    <div class="search-result-excerpt">${result.section}</div>
                </div>
            `;
        });
        searchResults.innerHTML = html;
        
        // 绑定点击事件
        searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                loadDoc(path);
                searchModal.classList.remove('active');
                const link = document.querySelector(`[data-path="${path}"]`);
                if (link) {
                    updateActiveLink(link);
                }
            });
        });
    }
}

// ==================== 图片预览 ====================
function initImageModal() {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const imageClose = document.getElementById('imageClose');
    const imageCaption = document.getElementById('imageCaption');
    
    imageClose.addEventListener('click', () => {
        imageModal.classList.remove('active');
    });
    
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) {
            imageModal.classList.remove('active');
        }
    });
}

function bindImageClick() {
    const images = document.querySelectorAll('.doc-article img');
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const imageCaption = document.getElementById('imageCaption');
    
    images.forEach(img => {
        img.addEventListener('click', () => {
            imageModal.classList.add('active');
            modalImage.src = img.src;
            imageCaption.textContent = img.alt || '';
        });
    });
}

// ==================== 键盘快捷键 ====================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: 打开搜索
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('searchModal').classList.add('active');
            document.getElementById('modalSearchInput').focus();
        }
        
        // ESC: 关闭模态框
        if (e.key === 'Escape') {
            document.getElementById('searchModal').classList.remove('active');
            document.getElementById('imageModal').classList.remove('active');
        }
    });
}

// ==================== 工具函数 ====================
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
