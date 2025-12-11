@echo off
chcp 65001 >nul
echo ========================================
echo    儿童识字小报生成器 - 一键测试
echo ========================================
echo.

REM 尝试不同的Python命令
echo [1/4] 查找Python...

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo ✓ 找到python命令
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        echo ✓ 找到py命令
    ) else (
        set PYTHON_CMD=python3
        echo ✓ 尝试使用python3命令
    )
)

echo.
echo [2/4] 运行环境测试...
%PYTHON_CMD% quick_test.py

echo.
echo [3/4] 检查Flask...
%PYTHON_CMD% -c "import flask; print('✓ Flask已安装')" 2>nul
if errorlevel 1 (
    echo ⚠ Flask未安装，正在尝试安装...
    %PYTHON_CMD% -m pip install flask
    if errorlevel 1 (
        echo ✗ Flask安装失败，请手动运行: pip install flask
        goto :end
    )
)

echo.
echo [4/4] 启动Web测试服务...
echo.
echo ========================================
echo 重要提示：
echo 1. 测试服务即将启动
echo 2. 浏览器会自动打开 http://localhost:5000
echo 3. 这是测试版，不需要API Key
echo 4. 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 等待3秒
timeout /t 3 /nobreak >nul

REM 尝试打开浏览器
start http://localhost:5000 2>nul

REM 启动测试服务
cd web
%PYTHON_CMD% test_app.py

:end
echo.
echo 按任意键退出...
pause >nul