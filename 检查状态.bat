@echo off
chcp 65001 >nul
cls
echo ========================================
echo    儿童识字小报生成器 - 状态检查
echo ========================================
echo.

REM 检查文件
echo [文件检查]
for %%f in (
    "src\main.py"
    "src\prompt_generator.py"
    "src\vocabulary.py"
    "src\api_client.py"
    "web\app.py"
    "web\test_app.py"
    "web\templates\index.html"
    "web\static\css\style.css"
    "web\static\js\main.js"
    "requirements.txt"
    ".env.example"
) do (
    if exist "%%f" (
        echo   ✓ %%f
    ) else (
        echo   ✗ %%f - [缺失]
    )
)

echo.
echo [目录检查]
if exist "src" echo   ✓ src目录
if exist "web" echo   ✓ web目录
if exist "config" echo   ✓ config目录
if exist "outputs" echo   ✓ outputs目录

echo.
echo [Python检查]
where python >nul 2>&1
if not errorlevel 1 (
    echo   ✓ Python已安装
    python --version 2>nul
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        echo   ✓ Python已安装(使用py命令)
        py --version 2>nul
    ) else (
        echo   ✗ Python未找到
    )
)

echo.
echo [环境配置]
if exist ".env" (
    echo   ✓ .env文件存在
    findstr "your_api_key_here" .env >nul 2>&1
    if not errorlevel 1 (
        echo   ⚠ 请在.env中配置真实的API Key
    ) else (
        echo   ✓ API Key已配置
    )
) else (
    echo   ⚠ .env文件不存在
    echo   复制.env.example为.env并配置API Key
)

echo.
echo ========================================
echo 快速启动指南：
echo.
echo 1. 简单测试（无API Key）:
echo    cd web
echo    python test_app.py
echo.
echo 2. 完整运行（需要API Key）:
echo    - 配置.env文件中的API Key
echo    - 双击 start_web.bat
echo.
echo 3. 或使用一键测试：
echo    双击 "一键测试.bat"
echo ========================================
echo.
pause