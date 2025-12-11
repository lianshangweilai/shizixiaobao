"""Flask Web应用 - 儿童识字小报生成器
在浏览器中运行的版本
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
import time
from datetime import datetime
import threading

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from prompt_generator import PromptGenerator
from api_client import APIClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 全局变量存储生成任务
generation_tasks = {}

# 初始化组件
prompt_generator = PromptGenerator()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/scenes', methods=['GET'])
def get_scenes():
    """获取所有可用场景"""
    scenes = prompt_generator.get_theme_suggestions()
    return jsonify({
        'success': True,
        'scenes': scenes
    })


@app.route('/api/preview', methods=['POST'])
def preview_prompt():
    """预览提示词"""
    data = request.json
    theme = data.get('theme', '')
    title = data.get('title', '')

    if not theme or not title:
        return jsonify({
            'success': False,
            'error': '请提供主题和标题'
        })

    try:
        prompt = prompt_generator.preview_prompt(theme, title)
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
    """生成图片"""
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
    api_key = os.getenv('KIE_AI_API_KEY')
    if not api_key:
        return jsonify({
            'success': False,
            'error': '未配置API Key'
        })

    # 生成任务ID
    task_id = f"task_{int(time.time())}"

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # 在后台线程中执行生成
    def generate_in_background():
        try:
            # 生成提示词
            prompt = prompt_generator.generate_prompt(theme, title)

            # 创建API客户端
            client = APIClient(api_key)

            # 生成图片
            output_path = client.generate_image(
                prompt=prompt,
                output_dir=output_dir,
                aspect_ratio=ratio,
                resolution=resolution,
                output_format=format_type,
                show_progress=False  # 禁用进度条
            )

            # 更新任务状态
            generation_tasks[task_id] = {
                'status': 'success',
                'output_path': os.path.basename(output_path),
                'message': '生成成功！'
            }

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
        'message': '正在生成中...'
    }

    return jsonify({
        'success': True,
        'task_id': task_id,
        'message': '任务已开始，请等待...'
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
        'error': task.get('error', '')
    })


@app.route('/outputs/<filename>')
def get_output_file(filename):
    """获取生成的图片"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    return send_file(os.path.join(output_dir, filename))


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取生成历史"""
    history_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs', 'history', 'generation_history.json'
    )

    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return jsonify({
                'success': True,
                'history': history[-20:]  # 返回最近20条
            })
        except:
            pass

    return jsonify({
        'success': True,
        'history': []
    })


if __name__ == '__main__':
    # 确保输出目录存在
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs'), exist_ok=True)

    # 运行Flask应用
    print("\n" + "="*60)
    print("儿童识字小报生成器 - Web版本")
    print("="*60)
    print(f"\n请在浏览器中打开: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)