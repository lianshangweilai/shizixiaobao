@echo off
chcp 65001 >nul
cls

echo ==========================================
echo    儿童识字小报生成器 - 正式版（修复版）
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

echo [1/3] 检查PIL库...
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PIL库...
    python -m pip install Pillow
)

echo [2/3] 检查其他依赖...
python -m pip install flask python-dotenv requests >nul 2>&1

echo [3/3] 启动服务器...
echo.
echo ==========================================
echo 🚀 正式版服务即将启动（已修复）
echo.
echo 📍 访问地址: http://localhost:5000
echo.
echo ✨ 修复内容：
echo   ✓ 图片显示问题已修复
echo   ✓ 下载功能已修复
echo   ✓ 双模式：演示模式 + 正式模式
echo   ✓ Base64 + URL 双重保障
echo   ✓ 完整的词汇标注
echo.
echo 🎯 使用说明：
echo   1. 演示模式：无需API Key，快速生成
echo   2. 正式模式：需要API Key，真实AI生成
echo   3. 生成后立即显示，可正常下载
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
python real_version.py

pause