"""测试Web应用的简化版本（不需要API Key）"""

from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# 模拟场景数据
MOCK_SCENES = ["超市", "医院", "公园", "学校", "动物园", "火车站"]

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/scenes', methods=['GET'])
def get_scenes():
    """获取所有可用场景"""
    return jsonify({
        'success': True,
        'scenes': MOCK_SCENES
    })

@app.route('/api/preview', methods=['POST'])
def preview_prompt():
    """预览提示词（模拟）"""
    return jsonify({
        'success': True,
        'prompt': "这是一个模拟的提示词预览..."
    })

@app.route('/api/generate', methods=['POST'])
def generate_image():
    """生成图片（模拟）"""
    return jsonify({
        'success': False,
        'error': '这是测试版本，请配置真实的API Key后再试'
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取生成历史（模拟）"""
    return jsonify({
        'success': True,
        'history': []
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("儿童识字小报生成器 - 测试版本")
    print("="*60)
    print(f"\n请在浏览器中打开: http://localhost:5000")
    print("\n注意：这是测试版本，需要配置API Key才能生成真实图片")
    print("按 Ctrl+C 停止服务")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)