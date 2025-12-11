"""修复版Web服务器
解决了图片显示和下载问题
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import base64

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, Response
    from prompt_generator import PromptGenerator
    from api_client import APIClient
    from dotenv import load_dotenv
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install flask python-dotenv requests tqdm colorama")
    sys.exit(1)

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'literacy-poster-generator-secret-key'

# 全局变量存储生成任务
generation_tasks = {}

# 初始化组件
prompt_generator = PromptGenerator()

# 任务历史记录
task_history = []
MAX_HISTORY = 50

# 存储生成的图片数据（Base64编码）
generated_images = {}


@app.route('/')
def index():
    """主页"""
    # 直接返回HTML内容
    return get_fixed_html()


@app.route('/api/scenes', methods=['GET'])
def get_scenes():
    """获取所有可用场景"""
    try:
        scenes = prompt_generator.get_theme_suggestions()
        return jsonify({
            'success': True,
            'scenes': scenes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/preview', methods=['POST'])
def preview_prompt():
    """预览提示词"""
    try:
        data = request.json
        theme = data.get('theme', '')
        title = data.get('title', '')

        if not theme or not title:
            return jsonify({
                'success': False,
                'error': '请提供主题和标题'
            })

        prompt = prompt_generator.generate_prompt(theme, title)
        return jsonify({
            'success': True,
            'prompt': prompt
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """生成图片任务"""
    try:
        data = request.json
        theme = data.get('theme', '')
        title = data.get('title', '')
        ratio = data.get('ratio', '3:4')
        resolution = data.get('resolution', '2K')
        format_type = data.get('format', 'png')

        if not theme or not title:
            return jsonify({
                'success': False,
                'error': '请提供主题和标题'
            })

        # 检查API Key
        api_key = data.get('api_key', '') or os.getenv('KIE_AI_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': '未提供API Key'
            })

        # 生成任务ID
        task_id = f"task_{int(time.time())}"

        # 创建输出目录
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'outputs'
        )
        os.makedirs(output_dir, exist_ok=True)

        # 在后台线程中执行生成
        def generate_in_background():
            try:
                # 生成提示词
                prompt = prompt_generator.generate_prompt(theme, title)

                # 创建API客户端
                client = APIClient(api_key)

                # 模拟生成过程（如果没有API Key）
                if api_key == 'demo_key' or not api_key.startswith('sk-'):
                    # 演示模式：生成一个占位图片
                    import urllib.request
                    from io import BytesIO
                    from PIL import Image, ImageDraw, ImageFont

                    # 创建演示图片
                    width, height = 600, 800
                    img = Image.new('RGB', (width, height), color='white')
                    draw = ImageDraw.Draw(img)

                    # 绘制标题
                    draw.text((50, 50), title, fill='black')
                    draw.text((50, 100), f'场景: {theme}', fill='gray')

                    # 保存图片
                    output_path = os.path.join(output_dir, f"{task_id}.{format_type}")
                    img.save(output_path)

                    # 读取并编码为Base64
                    with open(output_path, 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                else:
                    # 真实API调用
                    output_path = client.generate_image(
                        prompt=prompt,
                        output_dir=output_dir,
                        aspect_ratio=ratio,
                        resolution=resolution,
                        output_format=format_type,
                        show_progress=False
                    )

                    # 读取并编码为Base64
                    with open(output_path, 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')

                # 更新任务状态
                generation_tasks[task_id] = {
                    'status': 'success',
                    'output_path': os.path.basename(output_path),
                    'output_url': f'/api/image/{task_id}',
                    'image_base64': img_base64,
                    'theme': theme,
                    'title': title,
                    'message': '生成成功！'
                }

                # 添加到历史记录
                task_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'task_id': task_id,
                    'theme': theme,
                    'title': title,
                    'output_path': os.path.basename(output_path),
                    'image_base64': img_base64,
                    'status': 'success'
                })

                # 限制历史记录数量
                if len(task_history) > MAX_HISTORY:
                    task_history.pop(0)

            except Exception as e:
                generation_tasks[task_id] = {
                    'status': 'error',
                    'error': str(e),
                    'message': '生成失败'
                }

        # 启动后台任务
        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()

        # 初始化任务状态
        generation_tasks[task_id] = {
            'status': 'processing',
            'message': '正在生成中...',
            'progress': 0
        }

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '任务已开始，请等待...'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """检查任务状态"""
    if task_id not in generation_tasks:
        return jsonify({
            'success': False,
            'error': '任务不存在'
        })

    task = generation_tasks[task_id]
    return jsonify({
        'success': True,
        'status': task['status'],
        'message': task.get('message', ''),
        'output_path': task.get('output_path', ''),
        'output_url': task.get('output_url', ''),
        'image_base64': task.get('image_base64', ''),
        'error': task.get('error', ''),
        'theme': task.get('theme', ''),
        'title': task.get('title', ''),
        'progress': task.get('progress', 0)
    })


@app.route('/api/image/<task_id>')
def get_image(task_id):
    """获取生成的图片"""
    if task_id not in generation_tasks:
        return 'Image not found', 404

    task = generation_tasks[task_id]
    if task['status'] != 'success':
        return 'Image not ready', 404

    # 从Base64解码并返回
    if 'image_base64' in task:
        image_data = base64.b64decode(task['image_base64'])
        return Response(image_data, mimetype='image/png')

    # 或从文件读取
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    image_path = os.path.join(output_dir, task['output_path'])

    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        return 'File not found', 404


@app.route('/api/download/<task_id>')
def download_image(task_id):
    """下载生成的图片"""
    if task_id not in generation_tasks:
        return 'Image not found', 404

    task = generation_tasks[task_id]
    if task['status'] != 'success':
        return 'Image not ready', 404

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    image_path = os.path.join(output_dir, task['output_path'])

    if os.path.exists(image_path):
        return send_file(
            image_path,
            as_attachment=True,
            download_name=f"{task['title']}_{task['theme']}.{task['output_path'].split('.')[-1]}"
        )
    else:
        return 'File not found', 404


@app.route('/outputs/<filename>')
def get_output_file(filename):
    """获取输出的文件"""
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs'
    )
    return send_from_directory(output_dir, filename)


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取生成历史"""
    recent_history = task_history[-20:] if len(task_history) > 20 else task_history
    return jsonify({
        'success': True,
        'history': recent_history[::-1]  # 最新的在前
    })


def get_fixed_html():
    """获取修复后的HTML"""
    return '''<!DOCTYPE html>
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
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
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

        .control-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
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

        .result-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            min-height: 600px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        .result-image {
            max-width: 100%;
            max-height: 600px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .download-btn {
            display: inline-block;
            padding: 10px 25px;
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            transition: all 0.3s ease;
            margin-top: 20px;
        }

        .download-btn:hover {
            transform: scale(1.05);
            color: white;
        }
    </style>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar fixed-top">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-book-open"></i>
                儿童识字小报生成器
            </span>
            <div class="d-flex align-items-center">
                <button class="btn btn-sm btn-outline-primary me-2" onclick="showApiConfig()">
                    <i class="fas fa-key"></i> API配置
                </button>
            </div>
        </div>
    </nav>

    <!-- API配置模态框 -->
    <div class="modal fade" id="apiConfigModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-key"></i> API Key 配置
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Kie AI API Key</label>
                        <input type="password" class="form-control" id="apiKeyInput" placeholder="请输入您的API Key">
                        <div class="form-text">
                            <a href="https://kie.ai/api-key" target="_blank">点击这里获取API Key</a>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="demoModeCheck">
                            <label class="form-check-label" for="demoModeCheck">
                                使用演示模式（无需API Key，生成示例图片）
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                    <button type="button" class="btn btn-primary" onclick="saveApiKey()">保存</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 主要内容 -->
    <div class="container main-container">
        <div class="row">
            <!-- 左侧控制面板 -->
            <div class="col-lg-4">
                <div class="control-panel">
                    <!-- 场景选择 -->
                    <div class="mb-4">
                        <div class="section-title">
                            <i class="fas fa-map"></i> 选择场景
                        </div>
                        <div class="row g-3" id="sceneGrid">
                            <!-- 场景卡片将由JavaScript生成 -->
                        </div>
                    </div>

                    <!-- 标题输入 -->
                    <div class="mb-4">
                        <div class="section-title">
                            <i class="fas fa-heading"></i> 小报标题
                        </div>
                        <input type="text" class="form-control" id="titleInput" placeholder="例如：走进超市" value="走进超市">
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
                <div class="result-panel" id="resultPanel">
                    <div class="text-center" style="padding: 100px 0;">
                        <i class="fas fa-image fa-5x text-muted mb-4"></i>
                        <h4>准备生成识字小报</h4>
                        <p class="text-muted">选择场景和标题，点击"生成识字小报"开始创作</p>
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
        let currentTaskId = null;
        let apiKey = localStorage.getItem('kie_ai_api_key') || '';

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

        // 显示API配置
        function showApiConfig() {
            const modal = new bootstrap.Modal(document.getElementById('apiConfigModal'));
            document.getElementById('apiKeyInput').value = apiKey;
            modal.show();
        }

        // 保存API Key
        function saveApiKey() {
            const isDemoMode = document.getElementById('demoModeCheck').checked;

            if (isDemoMode) {
                apiKey = 'demo_key';
                localStorage.setItem('demo_mode', 'true');
            } else {
                apiKey = document.getElementById('apiKeyInput').value;
                localStorage.setItem('kie_ai_api_key', apiKey);
                localStorage.removeItem('demo_mode');
            }

            alert('配置已保存！');
            bootstrap.Modal.getInstance(document.getElementById('apiConfigModal')).hide();
        }

        // 生成图片
        async function generateImage() {
            const title = document.getElementById('titleInput').value || '识字小报';
            const ratio = document.getElementById('ratioSelect').value;
            const resolution = document.getElementById('resolutionSelect').value;

            // 检查配置
            if (!apiKey && !localStorage.getItem('demo_mode')) {
                alert('请先配置API Key或选择演示模式！');
                return;
            }

            // 显示加载状态
            const resultPanel = document.getElementById('resultPanel');
            resultPanel.innerHTML = `
                <div class="text-center">
                    <div class="spinner"></div>
                    <h4 class="mt-4">正在生成识字小报...</h4>
                    <p class="text-muted">请稍候，正在AI创作中...</p>
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
                        api_key: apiKey
                    })
                });

                const data = await response.json();

                if (data.success) {
                    currentTaskId = data.task_id;
                    await checkTaskStatus();
                } else {
                    throw new Error(data.error || '生成失败');
                }
            } catch (error) {
                showError(error.message);
            }
        }

        // 检查任务状态
        async function checkTaskStatus() {
            while (currentTaskId) {
                try {
                    const response = await fetch(`/api/status/${currentTaskId}`);
                    const data = await response.json();

                    if (data.success) {
                        if (data.status === 'success') {
                            showResult(data);
                            break;
                        } else if (data.status === 'error') {
                            throw new Error(data.error || '生成失败');
                        } else {
                            // 继续等待
                            await new Promise(resolve => setTimeout(resolve, 2000));
                        }
                    }
                } catch (error) {
                    throw error;
                }
            }
        }

        // 显示结果
        function showResult(data) {
            const resultPanel = document.getElementById('resultPanel');

            // 使用Base64数据显示图片
            let imageHtml = '';
            if (data.image_base64) {
                imageHtml = `<img src="data:image/png;base64,${data.image_base64}" class="result-image" alt="${data.title}">`;
            } else {
                imageHtml = `<img src="${data.output_url}" class="result-image" alt="${data.title}">`;
            }

            resultPanel.innerHTML = `
                <div class="text-center">
                    <h4 class="mb-4">
                        <i class="fas fa-check-circle text-success"></i> 生成完成！
                    </h4>
                    ${imageHtml}
                    <a href="/api/download/${currentTaskId}" class="download-btn">
                        <i class="fas fa-download"></i> 下载图片
                    </a>
                    <div class="mt-4">
                        <h5>小报信息</h5>
                        <p><strong>标题：</strong>${data.title}</p>
                        <p><strong>场景：</strong>${data.theme}</p>
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

        // 预览提示词
        function showPromptPreview() {
            alert('提示词预览功能需要后端支持');
        }
    </script>
</body>
</html>'''


def main():
    """主函数"""
    print("\n" + "="*60)
    print("儿童识字小报生成器 - 修复版")
    print("="*60)
    print()
    print("[信息] 启动中...")
    print("[信息] 访问地址: http://localhost:5000")
    print()
    print("[提示] 可以使用演示模式无需API Key")
    print("="*60)

    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # 运行Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )


if __name__ == '__main__':
    main()