"""简单可靠版本 - 确保图片正常显示和下载"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory, Response
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install flask Pillow")
    sys.exit(1)

# 创建Flask应用
app = Flask(__name__)

# 全局变量
generation_tasks = {}
task_history = []

# 内嵌HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>儿童识字小报生成器</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            font-family: 'Microsoft YaHei', sans-serif;
        }
        .main-container {
            padding-top: 80px;
            padding-bottom: 50px;
        }
        .card {
            border: none;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .scene-card {
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .scene-card:hover {
            border-color: #667eea;
            transform: translateY(-3px);
        }
        .scene-card.active {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }
        .result-image {
            max-width: 100%;
            max-height: 600px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .download-btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 500;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        .download-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(72, 187, 120, 0.4);
            color: white;
        }
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar fixed-top">
        <div class="container">
            <span class="navbar-brand fs-4">
                <i class="fas fa-book-open"></i> 儿童识字小报生成器
            </span>
        </div>
    </nav>

    <div class="container main-container">
        <div class="row">
            <!-- 左侧控制面板 -->
            <div class="col-lg-4">
                <div class="card p-4">
                    <h5 class="mb-3"><i class="fas fa-map"></i> 选择场景</h5>
                    <div class="row g-2 mb-4" id="sceneGrid">
                        <!-- 场景将由JS生成 -->
                    </div>

                    <h5 class="mb-3"><i class="fas fa-heading"></i> 小报标题</h5>
                    <input type="text" class="form-control mb-4" id="titleInput" value="走进超市" placeholder="输入标题">

                    <button class="btn btn-primary w-100 mb-2" onclick="generateImage()">
                        <i class="fas fa-magic"></i> 生成识字小报
                    </button>
                    <small class="text-muted">
                        <i class="fas fa-info-circle"></i> 生成时间约5-10秒
                    </small>
                </div>
            </div>

            <!-- 右侧结果区 -->
            <div class="col-lg-8">
                <div class="card p-4" style="min-height: 600px;">
                    <div id="resultPanel">
                        <div class="text-center" style="padding: 100px 0;">
                            <i class="fas fa-image fa-5x text-muted mb-4"></i>
                            <h4>准备生成识字小报</h4>
                            <p class="text-muted">选择场景和标题，点击生成按钮</p>
                        </div>
                    </div>
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

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            initScenes();
        });

        // 初始化场景
        function initScenes() {
            const grid = document.getElementById('sceneGrid');
            scenes.forEach((scene, index) => {
                const col = document.createElement('div');
                col.className = 'col-6';
                col.innerHTML = `
                    <div class="scene-card ${index === 0 ? 'active' : ''}" onclick="selectScene('${scene.name}', this)">
                        <i class="fas ${scene.icon} fa-2x mb-2"></i>
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

        // 生成图片
        async function generateImage() {
            const title = document.getElementById('titleInput').value || '识字小报';

            // 显示加载状态
            const resultPanel = document.getElementById('resultPanel');
            resultPanel.innerHTML = `
                <div class="text-center">
                    <div class="spinner"></div>
                    <h4 class="mt-3">正在生成识字小报...</h4>
                    <p class="text-muted">请稍候...</p>
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
                        title: title
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // 显示图片
                    showResult(data);
                } else {
                    showError(data.error || '生成失败');
                }
            } catch (error) {
                showError('网络错误：' + error.message);
            }
        }

        // 显示结果
        function showResult(data) {
            const resultPanel = document.getElementById('resultPanel');

            resultPanel.innerHTML = `
                <div class="text-center">
                    <h4 class="mb-4">
                        <i class="fas fa-check-circle text-success"></i> 生成完成！
                    </h4>
                    <img src="${data.image_url}" class="result-image" alt="${data.title}">
                    <a href="${data.download_url}" class="download-btn">
                        <i class="fas fa-download"></i> 下载图片
                    </a>
                    <div class="mt-4">
                        <h6>小报信息</h6>
                        <p class="mb-1"><strong>标题：</strong>${data.title}</p>
                        <p class="mb-1"><strong>场景：</strong>${data.theme}</p>
                        <p><strong>生成时间：</strong>${new Date().toLocaleString()}</p>
                    </div>
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
    </script>
</body>
</html>
'''

# 生成示例图片
def generate_sample_image(title, theme, task_id):
    """生成示例识字小报图片"""
    try:
        # 创建图片
        width, height = 600, 800
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 绘制标题背景
        draw.rectangle([0, 0, width, 100], fill='#667eea')

        # 绘制标题
        title_font_size = 48
        try:
            # Windows
            title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", title_font_size)
            text_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
        except:
            # 使用默认字体
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # 标题文字
        draw.text((width//2 - len(title)*12, 30), title, fill='white', font=title_font)

        # 绘制场景图片区域
        draw.rectangle([50, 150, width-50, 500], fill='#f0f0f0')

        # 场景图标
        draw.text((width//2 - 50, 250), f'主题：{theme}', fill='#333', font=text_font)

        # 生成示例词汇
        vocabularies = {
            '超市': ['收银员', '货架', '苹果', '牛奶'],
            '医院': ['医生', '护士', '药品', '病历'],
            '公园': ['花', '树', '秋千', '滑梯'],
            '学校': ['老师', '学生', '书本', '黑板'],
            '动物园': ['狮子', '猴子', '大象', '熊猫'],
            '火车站': ['列车', '站台', '乘客', '行李']
        }

        words = vocabularies.get(theme, ['词汇1', '词汇2', '词汇3', '词汇4'])

        # 绘制词汇
        y_pos = 550
        for i, word in enumerate(words):
            x_pos = 80 + (i % 2) * 250
            y = y_pos + (i // 2) * 80

            # 词汇框
            draw.rectangle([x_pos-10, y-20, x_pos+120, y+40], fill='#ffe4b5')
            draw.text((x_pos, y), word, fill='#333', font=text_font)

        # 保存图片
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
        os.makedirs(output_dir, exist_ok=True)

        image_path = os.path.join(output_dir, f"{task_id}.png")
        img.save(image_path, 'PNG', quality=95)

        return image_path

    except Exception as e:
        print(f"生成图片失败: {e}")
        return None


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

        # 生成任务ID
        task_id = f"task_{int(time.time())}"

        # 生成图片
        image_path = generate_sample_image(title, theme, task_id)

        if image_path and os.path.exists(image_path):
            # 转换为Base64（确保显示）
            with open(image_path, 'rb') as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')

            return jsonify({
                'success': True,
                'task_id': task_id,
                'title': title,
                'theme': theme,
                'image_url': f'/api/image/{task_id}',
                'download_url': f'/api/download/{task_id}',
                'image_base64': f"data:image/png;base64,{img_base64}"
            })
        else:
            return jsonify({
                'success': False,
                'error': '图片生成失败'
            })

    except Exception as e:
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
            download_name=f"识字小报_{task_id}.png"
        )
    else:
        return 'Image not found', 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("儿童识字小报生成器 - 简单版")
    print("="*60)
    print("\n启动中...")
    print("访问地址: http://localhost:5000")
    print("\n特点:")
    print("- 无需API Key")
    print("- 快速生成示例图片")
    print("- 确保图片正常显示和下载")
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