@echo off
:: 设置编码为 UTF-8
chcp 65001 >nul

:: 定义要检查的模块名称
set modules=pillow pyperclip requests tkinterdnd2

:: 指定 Python 和 pip 路径（确保替换成实际路径）
set PYTHON_PATH=python
set PIP_PATH=pip

:: 检查 pip 是否可用
%PIP_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到 pip，请确保 Python 已正确安装并将其添加到系统路径。
    pause
    exit /b
)

:: 创建 requirements.txt 文件
echo 正在生成 requirements.txt 文件...
(for %%i in (%modules%) do (
    %PIP_PATH% show %%i >nul 2>&1
    if %errorlevel% equ 0 (
        %PIP_PATH% show %%i | findstr "^Version:" >tmp.txt
        for /f "tokens=2 delims=: " %%j in (tmp.txt) do echo %%i==%%j
    ) else (
        echo %%i 未安装，无法导出版本信息。
    )
)) > requirements.txt
del tmp.txt 2>nul

:: 提示完成
if exist requirements.txt (
    echo requirements.txt 已成功生成。
    echo 文件位置: %cd%\requirements.txt
) else (
    echo 未能生成 requirements.txt，请检查 pip 配置。
)

:: 防止窗口立即关闭
pause
