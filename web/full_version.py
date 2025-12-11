"""完整的Web版本 - 支持真实的API调用
这是一个独立的Web服务器，可以直接运行使用
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from flask import Flask, render_template, request, jsonify, send_file
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
app.config['SECRET_KEY'] = ' literacy-poster-generator-secret-key'

# 全局变量存储生成任务
generation_tasks = {}

# 初始化组件
prompt_generator = PromptGenerator()

# 任务历史记录
task_history = []
MAX_HISTORY = 50


@app.route('/')
def index():
    """主页 - 返回正式版HTML"""
    return render_template('full_version.html')


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

                # 生成图片
                output_path = client.generate_image(
                    prompt=prompt,
                    output_dir=output_dir,
                    aspect_ratio=ratio,
                    resolution=resolution,
                    output_format=format_type,
                    show_progress=False
                )

                # 更新任务状态
                generation_tasks[task_id] = {
                    'status': 'success',
                    'output_path': os.path.basename(output_path),
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
        'error': task.get('error', ''),
        'theme': task.get('theme', ''),
        'title': task.get('title', ''),
        'progress': task.get('progress', 0)
    })


@app.route('/outputs/<filename>')
def get_output_file(filename):
    """获取生成的图片"""
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs'
    )
    return send_file(os.path.join(output_dir, filename))


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取生成历史"""
    # 返回最近20条记录
    recent_history = task_history[-20:] if len(task_history) > 20 else task_history
    return jsonify({
        'success': True,
        'history': recent_history[::-1]  # 最新的在前
    })


@app.route('/api/save-history', methods=['POST'])
def save_history_to_file():
    """保存历史记录到文件"""
    try:
        history_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'outputs',
            'history',
            'generation_history.json'
        )

        os.makedirs(os.path.dirname(history_file), exist_ok=True)

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(task_history, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': '历史记录已保存'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """处理配置"""
    if request.method == 'GET':
        # 获取配置信息
        return jsonify({
            'success': True,
            'config': {
                'api_key': '***' if os.getenv('KIE_AI_API_KEY') else None,
                'default_ratio': '3:4',
                'default_resolution': '2K',
                'supported_ratios': ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'],
                'supported_resolutions': ['1K', '2K', '4K'],
                'supported_formats': ['png', 'jpg']
            }
        })
    else:
        # 更新配置（POST）
        data = request.json
        if 'api_key' in data:
            # 这里应该安全地保存API Key
            # 但由于是演示版，暂时不实现
            pass
        return jsonify({
            'success': True,
            'message': '配置已更新'
        })


# 创建HTML模板
def create_template():
    """创建完整的HTML模板"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)

    template_path = os.path.join(template_dir, 'full_version.html')

    # 读取之前创建的正式版HTML
    source_html = os.path.join(os.path.dirname(os.path.dirname(__file__)), '正式版.html')

    if os.path.exists(source_html):
        with open(source_html, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修改为真实API调用
        content = content.replace(
            'async function generateImage() {',
            '''async function generateImage() {
                const apiKey = localStorage.getItem('kie_ai_api_key') || document.getElementById('apiKeyInput').value;
                if (!apiKey) {
                    alert('请先配置 API Key！\\n\\n点击右上角"API配置"按钮进行设置。');
                    return;
                }'''
        )

        content = content.replace(
            'await simulateGeneration();',
            '''// 调用真实API
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
                        format: format,
                        api_key: apiKey
                    })
                });

                const data = await response.json();

                if (data.success) {
                    currentTaskId = data.task_id;
                    await checkTaskStatus();
                } else {
                    throw new Error(data.error || '生成失败');
                }'''
        )

        # 添加任务状态检查函数
        status_check_function = '''
        // 检查任务状态
        async function checkTaskStatus() {
            while (currentTaskId) {
                try {
                    const response = await fetch(`/api/status/${currentTaskId}`);
                    const data = await response.json();

                    if (data.success) {
                        if (data.status === 'success') {
                            showRealResult(data.output_path, data.title, data.theme);
                            break;
                        } else if (data.status === 'error') {
                            throw new Error(data.error || '生成失败');
                        } else {
                            // 继续等待
                            updateProgress(data.progress || 0);
                            await sleep(2000);
                        }
                    }
                } catch (error) {
                    throw error;
                }
            }
        }

        // 显示真实结果
        function showRealResult(imagePath, title, theme) {
            const resultPanel = document.getElementById('resultPanel');

            resultPanel.innerHTML = `
                <div class="result-image-container">
                    <h4 class="mb-4">
                        <i class="fas fa-check-circle text-success"></i> 生成完成！
                    </h4>
                    <div style="position: relative; display: inline-block;">
                        <img src="/outputs/${imagePath}" class="result-image" alt="${title}">
                        <a href="/outputs/${imagePath}" download="${title}_${new Date().getTime()}.png" class="download-btn">
                            <i class="fas fa-download"></i> 下载
                        </a>
                    </div>
                    <div class="mt-4">
                        <h5>小报信息</h5>
                        <p><strong>标题：</strong>${title}</p>
                        <p><strong>场景：</strong>${theme}</p>
                        <p><strong>生成时间：</strong>${new Date().toLocaleString()}</p>
                    </div>
                </div>
            `;
        }

        // 更新进度
        function updateProgress(progress) {
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
        }

        // 延迟函数
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }'''

        # 在</script>前插入新函数
        content = content.replace('</script>', status_check_function + '\n</script>')

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"模板已创建: {template_path}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("儿童识字小报生成器 - Web正式版")
    print("="*60)
    print()

    # 创建HTML模板
    create_template()

    # 确保输出目录存在
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'outputs'
    )
    os.makedirs(output_dir, exist_ok=True)

    print(f"[信息] Web服务即将启动...")
    print(f"[信息] 请在浏览器中访问:")
    print(f"       http://localhost:5000")
    print()
    print(f"[信息] 重要提示:")
    print(f"       1. 需要配置 Kie AI API Key")
    print(f"       2. 获取API Key: https://kie.ai/api-key")
    print(f"       3. 按 Ctrl+C 停止服务")
    print("="*60 + "\n")

    # 运行Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()