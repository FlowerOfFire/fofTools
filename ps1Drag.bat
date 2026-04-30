@echo off
if "%~1"=="" (
    echo 请将 PS1 文件拖拽到此批处理文件上
    pause
    exit /b
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~1"

pause