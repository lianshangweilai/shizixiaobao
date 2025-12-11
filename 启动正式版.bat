@echo off
chcp 65001 >nul
cls

echo ==========================================
echo    儿童识字小报生成器 - 正式版启动器
echo ==========================================
echo.

REM 检查Python
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python！
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo ✓ Python环境正常

REM 检查依赖
echo.
echo [2/4] 检查依赖包...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在安装必要的依赖包...
    python -m pip install flask python-dotenv requests tqdm colorama
    if errorlevel 1 (
        echo ❌ 依赖安装失败！
        echo 请手动运行: pip install flask python-dotenv requests tqdm colorama
        pause
        exit /b 1
    )
)
echo ✓ 依赖包就绪

REM 检查.env文件
echo.
echo [3/4] 检查配置文件...
if not exist ".env" (
    echo ⚠ 未找到.env文件，正在创建...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ✓ 已创建.env文件
        echo ⚠ 请编辑.env文件，填入您的API Key
        echo   获取地址: https://kie.ai/api-key
    ) else (
        echo [注意] 请手动创建.env文件并配置API Key
    )
) else (
    echo ✓ 配置文件存在
)

REM 启动服务
echo.
echo [4/4] 启动Web服务...
echo.
echo ==========================================
echo 🚀 服务即将启动
echo.
echo 📍 访问地址: http://localhost:5000
echo.
echo 📋 使用说明:
echo   1. 配置API Key（首次使用）
echo   2. 选择场景和输入标题
echo   3. 点击生成按钮
echo   4. 等待30-60秒获取结果
echo.
echo ⏹️  按 Ctrl+C 停止服务
echo ==========================================
echo.

REM 等待2秒
timeout /t 2 /nobreak >nul

REM 尝试自动打开浏览器
echo 正在打开浏览器...
start http://localhost:5000 >nul 2>&1

REM 切换到web目录并启动
cd web
python full_version.py

REM 如果退出
echo.
echo 服务已停止
pause