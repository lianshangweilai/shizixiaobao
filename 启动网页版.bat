@echo off
chcp 65001 >nul
cls

echo.
echo ==========================================
echo        儿童识字小报生成器 - 启动中
echo ==========================================
echo.

REM 检查是否在正确的目录
if not exist "web\test_app.py" (
    echo 错误：请将此文件放在项目根目录运行！
    echo.
    pause
    exit /b 1
)

echo [步骤1] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 未找到Python！
    echo.
    echo 请先安装Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python 3.8+
    echo 3. 安装时勾选"Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✓ Python已找到

echo.
echo [步骤2] 安装Flask（如需要）...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在安装Flask，请稍候...
    python -m pip install flask --user
    if errorlevel 1 (
        echo ❌ Flask安装失败
        echo 请手动运行: pip install flask
        pause
        exit /b 1
    )
)
echo ✓ Flask已就绪

echo.
echo [步骤3] 启动Web服务器...
echo.
echo ==========================================
echo 重要提示：
echo 1. 服务器正在启动...
echo 2. 启动后会自动打开浏览器
echo 3. 如果没自动打开，请手动访问：
echo    http://localhost:5000
echo 4. 要停止服务，请关闭此窗口
echo ==========================================
echo.

REM 等待2秒
timeout /t 2 /nobreak >nul

REM 尝试自动打开浏览器
echo 正在打开浏览器...
start http://localhost:5000 >nul 2>&1

REM 切换到web目录并启动服务
cd web
echo.
echo 服务器运行中...
echo 访问地址: http://localhost:5000
echo.
python test_app.py

REM 如果程序退出，显示提示
echo.
echo 服务器已停止
pause