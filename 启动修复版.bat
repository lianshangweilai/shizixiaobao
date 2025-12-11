@echo off
chcp 65001 >nul
cls

echo ==========================================
echo    儿童识字小报生成器 - 修复版
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python！
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 安装PIL（用于演示模式）
echo [1/3] 检查PIL库...
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PIL库...
    python -m pip install Pillow
)

REM 检查其他依赖
echo [2/3] 检查其他依赖...
python -m pip install flask python-dotenv requests >nul 2>&1

REM 启动修复版服务器
echo [3/3] 启动服务器...
echo.
echo ==========================================
echo 🚀 修复版服务即将启动
echo.
echo 📍 访问地址: http://localhost:5000
echo.
echo ✨ 新特性：
echo   - 修复了图片显示问题
echo   - 修复了下载功能
echo   - 支持演示模式（无需API Key）
echo   - Base64编码确保图片正常显示
echo.
echo 按 Ctrl+C 停止服务
echo ==========================================
echo.

REM 等待2秒
timeout /t 2 /nobreak >nul

REM 自动打开浏览器
start http://localhost:5000 >nul 2>&1

REM 启动服务器
cd web
python fixed_version.py

pause