@echo off
chcp 65001 >nul
cls

echo ==========================================
echo    儿童识字小报生成器 - AI版本测试
echo ==========================================
echo.
echo 正在启动AI版本...
echo.

REM 自动打开AI版本HTML文件
start "" "C:\Users\hx\Desktop\图片生成器\AI版本.html"

echo.
echo ✨ AI版本已在浏览器中打开
echo.
echo 📝 测试步骤：
echo   1. 输入您的Kie AI API Key
echo   2. 选择场景和风格
echo   3. 点击"AI生成识字小报"
echo   4. 检查是否成功创建任务并生成图片
echo.
echo 🐛 修复内容：
echo   ✓ 修复了任务ID字段名（taskId vs task_id）
echo   ✓ 支持多种API响应格式
echo   ✓ 更新了查询参数名
echo.
pause