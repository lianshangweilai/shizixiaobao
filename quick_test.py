# 快速测试 - 无需安装任何东西
import sys
import os

print("="*60)
print("儿童识字小报生成器 - 快速测试")
print("="*60)

# 1. 检查Python版本
print(f"\nPython版本检查:")
try:
    print(f"当前版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if sys.version_info >= (3, 8):
        print("✓ Python版本满足要求")
    else:
        print("⚠ 需要Python 3.8或更高版本")
except:
    print("✗ 无法检测Python版本")

# 2. 检查文件结构
print("\n文件结构检查:")
required_files = [
    "src/main.py",
    "src/prompt_generator.py",
    "src/api_client.py",
    "src/vocabulary.py",
    "web/app.py",
    "web/test_app.py",
    "web/templates/index.html",
    "web/static/css/style.css",
    "web/static/js/main.js",
]

for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file}")
    else:
        print(f"✗ {file} - 缺失")

# 3. 测试提示词生成器
print("\n提示词生成器测试:")
try:
    sys.path.insert(0, 'src')
    from prompt_generator import PromptGenerator

    generator = PromptGenerator()
    prompt = generator.generate_prompt("超市", "走进超市", preview=True)
    print("✓ 提示词生成器工作正常")
    print(f"生成的提示词长度: {len(prompt)} 字符")
except Exception as e:
    print(f"✗ 提示词生成器错误: {e}")

# 4. 检查词汇库
print("\n词汇库检查:")
try:
    from vocabulary import VocabularyManager

    vocab = VocabularyManager()
    scenes = vocab.list_scenes()
    print(f"✓ 词汇库加载成功")
    print(f"可用场景数量: {len(scenes)}")
    print(f"场景列表: {', '.join(scenes)}")
except Exception as e:
    print(f"✗ 词汇库错误: {e}")

# 5. Web服务测试说明
print("\nWeb服务启动说明:")
print("-"*40)
print("1. 如果Flask已安装:")
print("   cd web")
print("   python test_app.py")
print("\n2. 如果Flask未安装:")
print("   pip install flask")
print("   然后运行上述命令")
print("\n3. 启动后访问: http://localhost:5000")
print("\n4. Ctrl+C 停止服务")

# 6. API Key配置提示
print("\nAPI Key配置:")
print("-"*40)
if os.path.exists('.env'):
    print("✓ .env 文件存在")
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_api_key_here' in content:
            print("⚠ 请在.env文件中填入真实的API Key")
        else:
            print("✓ API Key似乎已配置")
else:
    print("⚠ 未找到.env文件")
    print("请复制.env.example为.env并配置API Key")

print("\n" + "="*60)
print("测试完成！请按照上述说明启动Web服务")
print("="*60)

input("\n按Enter键退出...")