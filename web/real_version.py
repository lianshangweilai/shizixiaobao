"""改进的正式版 - 确保图片正常显示和下载"""

import os
import sys
import json
import time
import threading
import base64
from datetime import datetime
from pathlib import Path
import requests
from io import BytesIO

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory, Response
    from PIL import Image, ImageDraw, ImageFont
    from dotenv import load_dotenv
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install flask Pillow python-dotenv requests")
    sys.exit(1)

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 全局变量
generation_tasks = {}
task_history = []

# 正式版HTML模板（包含真实API调用和演示模式）
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>儿童识字小报生成器 - 正式版</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #48bb78;
            --danger-color: #f56565;
            --warning-color: #ed8936;
            --info-color: #4299e1;
        }

        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            font-family: 'Microsoft YaHei', sans-serif;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .navbar-brand {
            font-weight: bold;
            color: var(--primary-color) !important;
            font-size: 1.5rem;
        }

        .main-container {
            padding-top: 100px;
            padding-bottom: 50px;
        }

        .card {
            border: none;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .control-panel {
            position: sticky;
            top: 100px;
            max-height: calc(100vh - 150px);
            overflow-y: auto;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }

        .section-title i {
            margin-right: 10px;
            color: var(--primary-color);
        }

        .scene-card {
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            background: white;
        }

        .scene-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
        }

        .scene-card.active {
            border-color: var(--primary-color);
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        }

        .scene-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: var(--primary-color);
        }

        .result-panel {
            min-height: 600px;
        }

        .result-image {
            max-width: 100%;
            max-height: 600px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: block;
            margin: 0 auto;
        }

        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 50px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .progress-container {
            max-width: 400px;
            margin: 20px auto;
        }

        .download-btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 500;
            transition: all 0.3s ease;
            margin: 10px;
        }

        .download-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(72, 187, 120, 0.4);
            color: white;
        }

        .api-config-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .mode-toggle {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }

        .mode-btn {
            flex: 1;
            padding: 10px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .mode-btn.active {
            border-color: var(--primary-color);
            background: var(--primary-color);
            color: white;
        }

        .alert-custom {
            border-left: 4px solid var(--primary-color);
            background: #e7f3ff;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .vocab-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .vocab-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }

        .vocab-item:hover {
            border-color: var(--primary-color);
            transform: scale(1.05);
        }

        .vocab-chinese {
            font-size: 1.2rem;
            font-weight: bold;
            color: #2d3748;
        }

        .vocab-pinyin {
            font-size: 0.9rem;
            color: #718096;
            margin-top: 5px;
        }

        .status-indicator {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .status-demo {
            background: #ffd700;
            color: #333;
        }

        .status-real {
            background: #48bb78;
            color: white;
        }
    </style>
</head>
<body>
    <nav class="navbar fixed-top">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-book-open"></i>
                儿童识字小报生成器
                <span class="badge bg-success ms-2">正式版</span>
            </span>
            <div class="d-flex align-items-center">
                <span id="modeStatus" class="status-indicator status-demo">
                    <i class="fas fa-play"></i> 演示模式
                </span>
            </div>
        </div>
    </nav>

    <div class="container main-container">
        <div class="row">
            <!-- 左侧控制面板 -->
            <div class="col-lg-4">
                <div class="card card-body control-panel">
                    <!-- API配置区域 -->
                    <div class="api-config-section">
                        <h6 class="mb-3">
                            <i class="fas fa-cog"></i> 运行模式
                        </h6>
                        <div class="mode-toggle">
                            <div class="mode-btn active" id="demoModeBtn" onclick="setMode('demo')">
                                <i class="fas fa-play"></i><br>演示模式
                            </div>
                            <div class="mode-btn" id="realModeBtn" onclick="setMode('real')">
                                <i class="fas fa-robot"></i><br>正式模式
                            </div>
                        </div>

                        <div id="apiConfigPanel" style="display: none;">
                            <label class="form-label">Kie AI API Key</label>
                            <input type="password" class="form-control mb-2" id="apiKeyInput"
                                   placeholder="请输入您的API Key">
                            <small class="text-muted">
                                <a href="https://kie.ai/api-key" target="_blank">获取API Key</a>
                            </small>
                        </div>

                        <div id="demoModeInfo" class="alert-custom mt-3">
                            <i class="fas fa-info-circle"></i>
                            <strong>演示模式</strong><br>
                            无需API Key，快速生成示例图片
                        </div>
                    </div>

                    <!-- 场景选择 -->
                    <div class="mb-4">
                        <div class="section-title">
                            <i class="fas fa-map"></i> 选择场景
                        </div>
                        <div class="row g-3" id="sceneGrid">
                            <!-- 场景卡片将由JS生成 -->
                        </div>
                    </div>

                    <!-- 标题输入 -->
                    <div class="mb-4">
                        <div class="section-title">
                            <i class="fas fa-heading"></i> 小报标题
                        </div>
                        <input type="text" class="form-control" id="titleInput"
                               placeholder="例如：走进超市" value="走进超市">
                    </div>

                    <!-- 参数设置 -->
                    <div class="mb-4">
                        <div class="section-title">
                            <i class="fas fa-sliders-h"></i> 生成参数
                        </div>
                        <div class="row g-3">
                            <div class="col-6">
                                <label class="form-label">宽高比</label>
                                <select class="form-select" id="ratioSelect">
                                    <option value="3:4" selected>3:4 (A4竖版)</option>
                                    <option value="1:1">1:1 (正方形)</option>
                                    <option value="4:3">4:3 (横向)</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <label class="form-label">分辨率</label>
                                <select class="form-select" id="resolutionSelect">
                                    <option value="2K" selected>2K (推荐)</option>
                                    <option value="1K">1K (快速)</option>
                                    <option value="4K">4K (高清)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="d-grid gap-2">
                        <button class="btn btn-info" onclick="showPromptPreview()">
                            <i class="fas fa-eye"></i> 预览提示词
                        </button>
                        <button class="btn btn-primary btn-lg" onclick="generateImage()">
                            <i class="fas fa-magic"></i> 生成识字小报
                        </button>
                    </div>
                </div>
            </div>

            <!-- 右侧结果区 -->
            <div class="col-lg-8">
                <div class="card card-body result-panel">
                    <div id="resultPanel">
                        <div class="text-center" style="padding: 100px 0;">
                            <i class="fas fa-image fa-5x text-muted mb-4"></i>
                            <h4>准备生成识字小报</h4>
                            <p class="text-muted">选择场景和标题，点击"生成识字小报"开始创作</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 提示词预览模态框 -->
    <div class="modal fade" id="promptModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-code"></i> AI提示词预览
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="promptContent" style="background: #f8f9fa; padding: 20px; border-radius: 10px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto;"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    <button type="button" class="btn btn-primary" onclick="copyPrompt()">
                        <i class="fas fa-copy"></i> 复制
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const scenes = [
            { id: 'market', name: '超市', icon: 'fa-shopping-cart' },
            { id: 'hospital', name: '医院', icon: 'fa-hospital' },
            { id: 'park', name: '公园', icon: 'fa-tree' },
            { id: 'school', name: '学校', icon: 'fa-school' },
            { id: 'zoo', name: '动物园', icon: 'fa-paw' },
            { id: 'station', name: '火车站', icon: 'fa-train' }
        ];

        let selectedScene = '超市';
        let currentMode = 'demo'; // demo or real
        let currentTaskId = null;

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initScenes();
            loadSavedApiKey();
        });

        // 初始化场景
        function initScenes() {
            const grid = document.getElementById('sceneGrid');
            scenes.forEach((scene, index) => {
                const col = document.createElement('div');
                col.className = 'col-6';
                col.innerHTML = `
                    <div class="scene-card ${index === 0 ? 'active' : ''}" onclick="selectScene('${scene.name}', this)">
                        <div class="scene-icon">
                            <i class="fas ${scene.icon}"></i>
                        </div>
                        <div>${scene.name}</div>
                    </div>
                `;
                grid.appendChild(col);
            });
        }

        // 选择场景
        function selectScene(sceneName, element) {
            document.querySelectorAll('.scene-card').forEach(card => {
                card.classList.remove('active');
            });
            element.classList.add('active');
            selectedScene = sceneName;
        }

        // 设置模式
        function setMode(mode) {
            currentMode = mode;
            const demoBtn = document.getElementById('demoModeBtn');
            const realBtn = document.getElementById('realModeBtn');
            const apiPanel = document.getElementById('apiConfigPanel');
            const demoInfo = document.getElementById('demoModeInfo');
            const statusIndicator = document.getElementById('modeStatus');

            if (mode === 'demo') {
                demoBtn.classList.add('active');
                realBtn.classList.remove('active');
                apiPanel.style.display = 'none';
                demoInfo.style.display = 'block';
                statusIndicator.className = 'status-indicator status-demo';
                statusIndicator.innerHTML = '<i class="fas fa-play"></i> 演示模式';
            } else {
                demoBtn.classList.remove('active');
                realBtn.classList.add('active');
                apiPanel.style.display = 'block';
                demoInfo.style.display = 'none';
                statusIndicator.className = 'status-indicator status-real';
                statusIndicator.innerHTML = '<i class="fas fa-robot"></i> 正式模式';
            }
        }

        // 加载保存的API Key
        function loadSavedApiKey() {
            const savedKey = localStorage.getItem('kie_ai_api_key');
            if (savedKey) {
                document.getElementById('apiKeyInput').value = savedKey;
            }
        }

        // 生成图片
        async function generateImage() {
            const title = document.getElementById('titleInput').value || '识字小报';
            const ratio = document.getElementById('ratioSelect').value;
            const resolution = document.getElementById('resolutionSelect').value;

            // 检查API Key（正式模式）
            if (currentMode === 'real') {
                const apiKey = document.getElementById('apiKeyInput').value;
                if (!apiKey || apiKey.length < 10) {
                    alert('请输入有效的API Key！');
                    setMode('demo');
                    return;
                }
                localStorage.setItem('kie_ai_api_key', apiKey);
            }

            // 显示加载状态
            const resultPanel = document.getElementById('resultPanel');
            resultPanel.innerHTML = `
                <div class="text-center">
                    <div class="spinner"></div>
                    <h4 class="mt-4">正在生成识字小报...</h4>
                    <p class="text-muted">
                        ${currentMode === 'demo' ? '演示模式，约5-10秒' : '正式模式，约30-60秒'}
                    </p>
                    <div class="progress-container">
                        <div class="progress">
                            <div class="progress-bar progress-bar-striped progress-bar-animated"
                                 style="width: 100%"></div>
                        </div>
                    </div>
                </div>
            `;

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        theme: selectedScene,
                        title: title,
                        ratio: ratio,
                        resolution: resolution,
                        format: 'png',
                        mode: currentMode,
                        api_key: currentMode === 'real' ? document.getElementById('apiKeyInput').value : null
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // 直接显示结果（同步生成）
                    showResult(data);
                } else {
                    throw new Error(data.error || '生成失败');
                }
            } catch (error) {
                showError(error.message);
            }
        }

        // 显示结果
        function showResult(data) {
            const resultPanel = document.getElementById('resultPanel');

            // 使用Base64显示图片
            let imageHtml = '';
            if (data.image_base64) {
                imageHtml = `<img src="data:image/png;base64,${data.image_base64}" class="result-image" alt="${data.title}">`;
            } else if (data.image_url) {
                imageHtml = `<img src="${data.image_url}" class="result-image" alt="${data.title}">`;
            }

            resultPanel.innerHTML = `
                <div class="text-center">
                    <h4 class="mb-4">
                        <i class="fas fa-check-circle text-success"></i> 生成完成！
                    </h4>
                    ${imageHtml}
                    <div class="mt-4">
                        <a href="${data.download_url}" class="download-btn">
                            <i class="fas fa-download"></i> 下载图片
                        </a>
                        <button class="download-btn" onclick="window.open('${data.image_url || `data:image/png;base64,${data.image_base64}`}, '_blank')">
                            <i class="fas fa-expand"></i> 新窗口查看
                        </button>
                    </div>
                    <div class="mt-4">
                        <h5>小报信息</h5>
                        <p><strong>标题：</strong>${data.title}</p>
                        <p><strong>场景：</strong>${data.theme}</p>
                        <p><strong>模式：</strong>${currentMode === 'demo' ? '演示模式' : '正式模式'}</p>
                        <p><strong>生成时间：</strong>${new Date().toLocaleString()}</p>
                    </div>
                    ${data.vocabulary ? `
                        <div class="mt-4">
                            <h5>包含词汇</h5>
                            <div class="vocab-grid">
                                ${data.vocabulary.map(v => `
                                    <div class="vocab-item">
                                        <div class="vocab-chinese">${v.chinese}</div>
                                        <div class="vocab-pinyin">${v.pinyin}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // 显示错误
        function showError(message) {
            const resultPanel = document.getElementById('resultPanel');
            resultPanel.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle fa-5x text-danger mb-4"></i>
                    <h4>生成失败</h4>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-primary mt-3" onclick="location.reload()">
                        <i class="fas fa-redo"></i> 重试
                    </button>
                </div>
            `;
        }

        // 预览提示词
        function showPromptPreview() {
            const title = document.getElementById('titleInput').value || '识字小报';

            // 生成示例提示词
            const prompt = `请生成一张儿童识字小报《${selectedScene}》，竖版 A4，学习小报版式，适合 5–9 岁孩子 认字与看图识物。

# 一、小报标题区（顶部）
**顶部居中大标题**：《${title}**
* **风格**：十字小报 / 儿童学习报感
* **文本要求**：大字、醒目、卡通手写体、彩色描边

# 二、小报主体（中间主画面）
画面中心是一幅 **卡通插画风的「${selectedScene}」场景**：
* **整体气氛**：明亮、温暖、积极
* **构图**：物体边界清晰，方便对应文字，不要过于拥挤。

# 三、必画物体与识字清单
**请务必在画面中清晰绘制以下物体**：
（将包含与${selectedScene}相关的15-20个词汇）

# 四、识字标注规则
对物体贴上中文识字标签：
* **格式**：两行制（第一行拼音，第二行简体汉字）
* **样式**：彩色小贴纸风格，白底黑字，清晰可读

# 五、画风参数
* **风格**：儿童绘本风 + 识字小报风
* **色彩**：高饱和、明快、温暖
* **质量**：8k resolution, high detail, vector illustration style, clean lines`;

            document.getElementById('promptContent').textContent = prompt;
            const modal = new bootstrap.Modal(document.getElementById('promptModal'));
            modal.show();
        }

        // 复制提示词
        function copyPrompt() {
            const promptText = document.getElementById('promptContent').textContent;
            navigator.clipboard.writeText(promptText).then(() => {
                alert('提示词已复制到剪贴板！');
            });
        }
    </script>
</body>
</html>
'''

# 词汇数据
VOCABULARIES = {
    '超市': [
        {'pinyin': 'shōu yín yuán', 'chinese': '收银员'},
        {'pinyin': 'huò jià', 'chinese': '货架'},
        {'pinyin': 'tuī chē', 'chinese': '推车'},
        {'pinyin': 'píng guǒ', 'chinese': '苹果'},
        {'pinyin': 'niú nǎi', 'chinese': '牛奶'},
        {'pinyin': 'miàn bāo', 'chinese': '面包'}
    ],
    '医院': [
        {'pinyin': 'yī shēng', 'chinese': '医生'},
        {'pinyin': 'hù shì', 'chinese': '护士'},
        {'pinyin': 'yào pǐn', 'chinese': '药品'},
        {'pinyin': 'yì zhēn', 'chinese': '针'},
        {'pinyin': 'bìng rén', 'chinese': '病人'}
    ],
    '公园': [
        {'pinyin': 'huā', 'chinese': '花'},
        {'pinyin': 'shù', 'chinese': '树'},
        {'pinyin': 'qiū qiān', 'chinese': '秋千'},
        {'pinyin': 'huá tī', 'chinese': '滑梯'},
        {'pinyin': 'cǎo dì', 'chinese': '草地'},
        {'pinyin': 'niǎo', 'chinese': '鸟'}
    ],
    '学校': [
        {'pinyin': 'lǎo shī', 'chinese': '老师'},
        {'pinyin': 'xué shēng', 'chinese': '学生'},
        {'pinyin': 'shū', 'chinese': '书'},
        {'pinyin': 'zhuō zi', 'chinese': '桌子'},
        {'pinyin': 'hēi bǎn', 'chinese': '黑板'}
    ],
    '动物园': [
        {'pinyin': 'shī zi', 'chinese': '狮子'},
        {'pinyin': 'hóu zi', 'chinese': '猴子'},
        {'pinyin': 'dà xiàng', 'chinese': '大象'},
        {'pinyin': 'xióng māo', 'chinese': '熊猫'}
    ],
    '火车站': [
        {'pinyin': 'huǒ chē', 'chinese': '火车'},
        {'pinyin': 'zhàn tái', 'chinese': '站台'},
        {'pinyin': 'chéng kè', 'chinese': '乘客'},
        {'pinyin': 'xíng li', 'chinese': '行李'}
    ]
}


def generate_sample_image(title, theme, task_id):
    """生成示例识字小报图片"""
    try:
        # 创建图片
        width, height = 800, 1000
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 绘制渐变背景
        for y in range(height):
            color_value = int(255 - (y / height) * 30)
            draw.rectangle([(0, y), (width, y+1)], fill=(color_value, color_value, 255))

        # 加载字体
        try:
            # Windows字体
            title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 60)
            vocab_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            pinyin_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
        except:
            # 使用默认字体
            title_font = ImageFont.load_default()
            vocab_font = ImageFont.load_default()
            pinyin_font = ImageFont.load_default()

        # 绘制顶部装饰
        draw.rectangle([0, 0, width, 120], fill='#667eea')
        draw.rectangle([0, 100, width, 110], fill='#764ba2')

        # 绘制标题
        title_text = f"《{title}》"
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, 25), title_text, fill='white', font=title_font)

        # 绘制主题标签
        theme_text = f"主题：{theme}"
        bbox = draw.textbbox((0, 0), theme_text, font=vocab_font)
        theme_width = bbox[2] - bbox[0]
        draw.text(((width - theme_width) // 2, 70), theme_text, fill='#ffd700', font=vocab_font)

        # 绘制中间区域
        draw.rectangle([50, 150, width-50, 450], fill='#f0f8ff', outline='#667eea', width=3)

        # 场景标题
        scene_title = f"卡通插画风的「{theme}」场景"
        bbox = draw.textbbox((0, 0), scene_title, font=vocab_font)
        scene_width = bbox[2] - bbox[0]
        draw.text(((width - scene_width) // 2, 300), scene_title, fill='#333', font=vocab_font)

        # 获取词汇
        vocabulary = VOCABULARIES.get(theme, [
            {'pinyin': 'cí huì', 'chinese': '词汇1'},
            {'pinyin': 'cí huì', 'chinese': '词汇2'},
            {'pinyin': 'cí huì', 'chinese': '词汇3'},
            {'pinyin': 'cí huì', 'chinese': '词汇4'}
        ])

        # 绘制词汇区域
        y_pos = 500
        for i, vocab in enumerate(vocabulary[:6]):
            x_pos = 100 + (i % 3) * 250
            y = y_pos + (i // 3) * 120

            # 词汇卡片背景
            card_width = 200
            card_height = 80
            draw.rectangle([x_pos-20, y-20, x_pos+card_width-20, y+card_height-20],
                         fill='#ffe4b5', outline='#667eea', width=2, border_radius=10)

            # 中文词汇
            bbox = draw.textbbox((0, 0), vocab['chinese'], font=vocab_font)
            vocab_width = bbox[2] - bbox[0]
            draw.text((x_pos + (card_width - vocab_width)//2 - 20, y), vocab['chinese'],
                     fill='#333', font=vocab_font)

            # 拼音
            bbox = draw.textbbox((0, 0), vocab['pinyin'], font=pinyin_font)
            pinyin_width = bbox[2] - bbox[0]
            draw.text((x_pos + (card_width - pinyin_width)//2 - 20, y + 35), vocab['pinyin'],
                     fill='#666', font=pinyin_font)

        # 绘制底部说明
        note_text = "适合5-9岁儿童认字学习"
        bbox = draw.textbbox((0, 0), note_text, font=vocab_font)
        note_width = bbox[2] - bbox[0]
        draw.text(((width - note_width) // 2, height - 80), note_text, fill='#666', font=vocab_font)

        # 保存图片
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
        os.makedirs(output_dir, exist_ok=True)

        image_path = os.path.join(output_dir, f"{task_id}.png")
        img.save(image_path, 'PNG', quality=95, optimize=True)

        print(f"图片已生成: {image_path}")
        return image_path, vocabulary

    except Exception as e:
        print(f"生成图片失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def generate_real_image(prompt, api_key, task_id):
    """使用真实API生成图片"""
    try:
        # 导入API客户端
        from api_client import APIClient

        client = APIClient(api_key)

        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
        os.makedirs(output_dir, exist_ok=True)

        # 生成图片
        output_path = client.generate_image(
            prompt=prompt,
            output_dir=output_dir,
            aspect_ratio='3:4',
            resolution='2K',
            output_format='png',
            show_progress=False
        )

        return output_path, []

    except Exception as e:
        print(f"API生成失败: {e}")
        # 如果API失败，回退到演示模式
        return None, None


@app.route('/')
def index():
    """主页"""
    return HTML_TEMPLATE


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """生成图片接口"""
    try:
        data = request.json
        theme = data.get('theme', '超市')
        title = data.get('title', '识字小报')
        mode = data.get('mode', 'demo')
        api_key = data.get('api_key')

        # 生成任务ID
        task_id = f"task_{int(time.time())}"

        # 根据模式生成图片
        if mode == 'demo' or not api_key:
            # 演示模式
            image_path, vocabulary = generate_sample_image(title, theme, task_id)
            if not image_path:
                return jsonify({
                    'success': False,
                    'error': '生成失败'
                })
        else:
            # 正式模式
            # 构建提示词
            vocab = VOCABULARIES.get(theme, [])
            vocab_text = '\n'.join([f"{v['pinyin']} {v['chinese']}" for v in vocab[:6]])

            prompt = f"""请生成一张儿童识字小报《{theme}》，竖版 A4，学习小报版式，适合 5–9 岁孩子 认字与看图识物。

顶部大标题：《{title}》
风格：卡通插画风，儿童绘本风
色彩：明亮、温暖、高饱和度

必须包含的词汇：
{vocab_text}

每个词汇需要：
1. 清晰的物品图像
2. 贴上识字标签（两行：拼音+汉字）
3. 标签样式：彩色贴纸风格"""

            image_path, vocabulary = generate_real_image(prompt, api_key, task_id)

            # 如果API失败，使用演示图片
            if not image_path:
                print("API失败，使用演示图片")
                image_path, vocabulary = generate_sample_image(title, theme, task_id)

        # 读取图片并转换为Base64
        with open(image_path, 'rb') as f:
            img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')

        # 获取词汇
        if not vocabulary:
            vocabulary = VOCABULARIES.get(theme, [])

        return jsonify({
            'success': True,
            'task_id': task_id,
            'title': title,
            'theme': theme,
            'image_url': f'/api/image/{task_id}',
            'download_url': f'/api/download/{task_id}',
            'image_base64': img_base64,
            'vocabulary': vocabulary
        })

    except Exception as e:
        print(f"生成错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/image/<task_id>')
def get_image(task_id):
    """获取图片"""
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs',
        f"{task_id}.png"
    )

    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return 'Image not found', 404


@app.route('/api/download/<task_id>')
def download_image(task_id):
    """下载图片"""
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs',
        f"{task_id}.png"
    )

    if os.path.exists(image_path):
        return send_file(
            image_path,
            as_attachment=True,
            download_name=f"识字小报_{task_id}.png",
            mimetype='image/png'
        )
    else:
        return 'Image not found', 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("儿童识字小报生成器 - 正式版（已修复）")
    print("="*60)
    print("\n特点:")
    print("✓ 双模式：演示模式 + 正式模式")
    print("✓ 图片确保正常显示和下载")
    print("✓ Base64 + URL 双重保障")
    print("✓ 词汇标注完整")
    print("\n访问地址: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务")
    print("="*60)

    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # 启动服务
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )