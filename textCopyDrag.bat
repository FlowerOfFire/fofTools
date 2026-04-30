@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo 请将文本文件拖拽到此脚本上运行
    pause
    exit /b
)

set "filepath=%~1"
set "filename=%~nx1"

echo 正在处理文件: !filename!
echo 文件路径: !filepath!

if not exist "!filepath!" (
    echo 错误: 文件不存在
    echo 请检查文件路径是否正确
    pause
    exit /b
)

rem 创建临时文件来构建输出
set "tempfile=%temp%\format_output_%random%.txt"

echo 文本文件：> "!tempfile!"
echo !filepath!>> "!tempfile!"
echo ````>> "!tempfile!"
type "!filepath!" >> "!tempfile!"
echo.>> "!tempfile!"
echo ````>> "!tempfile!"

rem 将临时文件内容复制到剪贴板
type "!tempfile!" | clip

del "!tempfile!"

echo.
echo 已成功复制到剪贴板！
echo.
echo 格式示例:
echo 文本文件：
echo !filepath!
echo ````
echo ^(文件内容^)
echo ````
echo.
REM pause
