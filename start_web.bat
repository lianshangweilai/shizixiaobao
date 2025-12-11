@echo off
REM 儿童识字小报生成器 - Web版本启动脚本
echo ========================================
echo     儿童识字小报生成器 v1.0
echo           Web 浏览器版本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo 请确保已安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查并安装依赖
echo [检查] 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装Web依赖包...
    pip install flask python-dotenv requests tqdm colorama
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
)

REM 检查是否存在.env文件
if not exist ".env" (
    echo [警告] 未找到.env配置文件！
    echo 正在从.env.example创建...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [提示] 请编辑.env文件，填入您的Kie AI API Key
        echo API Key获取地址：https://kie.ai/api-key
    )
    echo.
)

REM 启动Web服务
echo.
echo [启动] 正在启动Web服务...
echo.
echo ========================================
echo 重要提示：
echo 1. 程序启动后，会在浏览器中自动打开
echo 2. 如果没有自动打开，请手动访问：
echo    http://localhost:5000
echo 3. 按 Ctrl+C 可以停止服务
echo ========================================
echo.

REM 等待2秒后自动打开浏览器
timeout /t 2 /nobreak >nul
start http://localhost:5000

REM 运行Flask应用
cd web
python app.py

pause