@echo off
setlocal enabledelayedexpansion
cls
title 无限循环运行PS1脚本工具
echo ==================================================
echo          无限循环运行PowerShell脚本工具
echo  使用方法：将 .ps1 文件拖拽到本脚本上运行
echo ==================================================
echo.

:: 检查是否拖拽了文件
if "%~1"=="" (
    echo 【错误】请将 .ps1 脚本文件拖拽到本批处理上！
    echo.
    pause
    exit /b
)

:: ==============================================
:: 第一步：把所有拖拽的文件存入列表（解决无限循环需要复用参数）
:: ==============================================
set "fileList="
set "fileCount=0"
for %%i in (%*) do (
    set /a fileCount+=1
    set "fileList=!fileList! "%%i""
)

:: 修复文件数量显示
echo 已拖拽 !fileCount! 个文件，开始【无限循环】执行...
echo.
echo 【说明】执行完最后一个会自动回到第一个，关闭窗口即停止
echo.

:: ==============================================
:: 第二步：无限循环执行列表中的文件
:: ==============================================
:LOOP_START
for %%f in (!fileList!) do (
    if /i "%%~xf"==".ps1" (
        echo ==================================================
        echo 正在执行：%%~nxf
        echo ==================================================
        echo.
        
        :: 运行PowerShell脚本（绕过权限限制）
        powershell -ExecutionPolicy Bypass -File "%%f"
        
        :: 执行完/终止后暂停
        echo.
        echo 【当前脚本已结束】按任意键继续下一个...
        pause >nul
        echo.
        echo --------------------------------------------------
        echo.
    ) else (
        echo 【跳过】非PS1文件：%%~nxf
        echo.
    )
)

:: 关键：跳回开头，无限循环
goto LOOP_START