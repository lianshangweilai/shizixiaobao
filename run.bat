@echo off
REM 儿童识字小报生成器启动脚本
echo ========================================
echo     儿童识字小报生成器 v1.0
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

REM 检查依赖
echo [检查] 检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
)

REM 运行主程序
echo.
echo [运行] 启动儿童识字小报生成器...
echo.
python src\main.py %*

pause