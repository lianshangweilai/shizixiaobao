#!/usr/bin/env python3
"""检查Python环境和安装依赖的脚本"""
import sys
import subprocess
import importlib
import os

def check_python_version():
    """检查Python版本"""
    print(f"当前Python版本: {sys.version}")
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    return True

def check_package(package_name):
    """检查包是否已安装"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装包"""
    print(f"正在安装 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package_name} 安装失败: {e}")
        return False

def main():
    print("="*60)
    print("儿童识字小报生成器 - 环境检查工具")
    print("="*60)
    print()

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    # 需要的包列表
    packages = [
        ("requests", "HTTP请求库"),
        ("python-dotenv", "环境变量管理"),
        ("tqdm", "进度条显示"),
        ("colorama", "命令行颜色"),
        ("flask", "Web框架"),
    ]

    print("\n检查依赖包:")
    print("-"*40)

    # 检查并安装缺失的包
    all_installed = True
    for package, description in packages:
        if check_package(package):
            print(f"✓ {package} - {description}")
        else:
            print(f"✗ {package} - {description} (未安装)")
            all_installed = False

    if not all_installed:
        print("\n开始安装缺失的包...")
        print("-"*40)

        for package, _ in packages:
            if not check_package(package):
                if not install_package(package):
                    print(f"\n安装 {package} 失败，请手动运行:")
                    print(f"pip install {package}")
                    sys.exit(1)

    print("\n✓ 所有依赖已就绪！")
    print("\n现在可以运行以下命令启动Web服务:")
    print("cd web")
    print("python app.py")
    print("\n或者双击 start_web.bat 文件")

if __name__ == "__main__":
    main()