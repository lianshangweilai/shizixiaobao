@echo off
chcp 65001 >nul
cls

echo ==========================================
echo    儿童识字小报生成器 - 简单版
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python！
    echo 请先安装Python
    pause
    exit /b 1
)

REM 安装依赖
echo [1/2] 检查依赖包...
python -m pip install flask Pillow >nul 2>&1

REM 启动服务
echo [2/2] 启动服务器...
echo.
echo ==========================================
echo 🚀 服务即将启动
echo.
echo 📍 访问地址: http://localhost:5000
echo.
echo ✨ 特点：
echo   - 无需配置
echo   - 无需API Key
echo   - 5-10秒生成
echo   - 图片正常显示
echo   - 支持下载
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
python simple_version.py

pause