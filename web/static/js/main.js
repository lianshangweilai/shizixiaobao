// 儿童识字小报生成器 - 前端JavaScript

// 全局变量
let currentTaskId = null;
let statusCheckInterval = null;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载场景列表
    loadScenes();

    // 加载历史记录
    loadHistory();

    // 绑定表单事件
    document.getElementById('generateForm').addEventListener('submit', handleGenerate);
    document.getElementById('previewBtn').addEventListener('click', handlePreview);
    document.getElementById('downloadBtn').addEventListener('click', handleDownload);
});

// 加载所有可用场景
async function loadScenes() {
    try {
        const response = await fetch('/api/scenes');
        const data = await response.json();

        if (data.success) {
            const themeSelect = document.getElementById('theme');
            data.scenes.forEach(scene => {
                const option = document.createElement('option');
                option.value = scene;
                option.textContent = scene;
                themeSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载场景失败:', error);
        showError('加载场景列表失败');
    }
}

// 加载生成历史
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        if (data.success && data.history.length > 0) {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';

            // 显示最近6条历史记录
            data.history.slice(-6).reverse().forEach(item => {
                const col = document.createElement('div');
                col.className = 'col-md-4';

                const card = document.createElement('div');
                card.className = 'card history-item fade-in';
                card.innerHTML = `
                    <img src="/outputs/${item.output_path}" class="card-img-top" alt="${item.title}">
                    <div class="card-body p-2">
                        <h6 class="card-title small mb-1">${item.title}</h6>
                        <p class="card-text small text-muted mb-0">${item.theme}</p>
                    </div>
                `;

                card.addEventListener('click', () => {
                    showImageResult(item.output_path, item.title, item.theme);
                });

                col.appendChild(card);
                historyList.appendChild(col);
            });
        }
    } catch (error) {
        console.error('加载历史记录失败:', error);
    }
}

// 处理生成请求
async function handleGenerate(e) {
    e.preventDefault();

    // 获取表单数据
    const theme = document.getElementById('theme').value;
    const title = document.getElementById('title').value;
    const ratio = document.getElementById('ratio').value;
    const resolution = document.getElementById('resolution').value;

    if (!theme || !title) {
        showError('请填写主题和标题');
        return;
    }

    // 隐藏之前的错误和结果
    hideAllSections();

    // 显示状态区域
    showStatus('正在提交生成任务...');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                theme: theme,
                title: title,
                ratio: ratio,
                resolution: resolution,
                format: 'png'
            })
        });

        const data = await response.json();

        if (data.success) {
            currentTaskId = data.task_id;
            showStatus(data.message);
            // 开始轮询任务状态
            startStatusPolling();
        } else {
            showError(data.error || '提交任务失败');
        }
    } catch (error) {
        console.error('生成失败:', error);
        showError('网络错误，请重试');
    }
}

// 处理预览请求
async function handlePreview() {
    const theme = document.getElementById('theme').value;
    const title = document.getElementById('title').value;

    if (!theme || !title) {
        showError('请先填写主题和标题');
        return;
    }

    try {
        const response = await fetch('/api/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                theme: theme,
                title: title
            })
        });

        const data = await response.json();

        if (data.success) {
            // 显示提示词预览
            document.getElementById('promptPreview').textContent = data.prompt;
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            modal.show();
        } else {
            showError(data.error || '预览失败');
        }
    } catch (error) {
        console.error('预览失败:', error);
        showError('网络错误，请重试');
    }
}

// 开始轮询任务状态
function startStatusPolling() {
    statusCheckInterval = setInterval(async () => {
        if (!currentTaskId) return;

        try {
            const response = await fetch(`/api/status/${currentTaskId}`);
            const data = await response.json();

            if (data.success) {
                if (data.status === 'success') {
                    // 生成成功
                    clearInterval(statusCheckInterval);
                    hideStatus();
                    showImageResult(data.output_path,
                                 document.getElementById('title').value,
                                 document.getElementById('theme').value);
                    // 刷新历史记录
                    setTimeout(loadHistory, 1000);
                } else if (data.status === 'error') {
                    // 生成失败
                    clearInterval(statusCheckInterval);
                    hideStatus();
                    showError(data.error || '生成失败');
                } else {
                    // 仍在处理中
                    showStatus(data.message || '正在生成中...');
                }
            }
        } catch (error) {
            console.error('检查状态失败:', error);
        }
    }, 2000); // 每2秒检查一次
}

// 显示图片结果
function showImageResult(imagePath, title, theme) {
    const resultSection = document.getElementById('resultSection');
    const resultImage = document.getElementById('resultImage');
    const resultTitle = document.getElementById('resultTitle');
    const resultTheme = document.getElementById('resultTheme');

    resultImage.src = `/outputs/${imagePath}`;
    resultTitle.textContent = title;
    resultTheme.textContent = `主题：${theme}`;

    // 设置下载链接
    document.getElementById('downloadBtn').onclick = () => {
        window.open(`/outputs/${imagePath}`, '_blank');
    };

    resultSection.style.display = 'block';
    resultSection.classList.add('fade-in');

    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// 显示状态
function showStatus(message) {
    const statusSection = document.getElementById('statusSection');
    const statusText = document.getElementById('statusText');

    statusText.textContent = message;
    statusSection.style.display = 'block';
    statusSection.classList.add('fade-in');
}

// 隐藏状态
function hideStatus() {
    const statusSection = document.getElementById('statusSection');
    statusSection.style.display = 'none';
}

// 显示错误
function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    errorSection.classList.add('fade-in');

    // 自动隐藏错误信息
    setTimeout(() => {
        errorSection.style.display = 'none';
    }, 5000);
}

// 隐藏所有区域
function hideAllSections() {
    hideStatus();
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

// 处理下载
function handleDownload() {
    const resultImage = document.getElementById('resultImage');
    if (resultImage.src) {
        // 创建临时链接下载
        const link = document.createElement('a');
        link.href = resultImage.src;
        link.download = resultImage.src.split('/').pop();
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}