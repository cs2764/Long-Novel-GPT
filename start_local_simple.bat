@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM Long-Novel-GPT Windows 简化启动脚本
REM Windows Simplified Startup Script

REM 配置
set DEFAULT_ENV_NAME=long-novel-gpt
set DEFAULT_PYTHON_VERSION=3.10
set BACKEND_PORT=7869
set FRONTEND_PORT=8080
set BACKEND_HOST=127.0.0.1

echo ==============================================
echo Long-Novel-GPT Windows 启动器
echo ==============================================
echo.

REM 检查conda是否安装
where conda >nul 2>&1
if errorlevel 1 (
    echo [错误] Conda 未安装或未添加到PATH
    echo 请先安装 Anaconda 或 Miniconda
    echo 下载地址: https://www.anaconda.com/products/distribution
    echo.
    pause
    exit /b 1
)

echo [成功] Conda 已安装

REM 检查虚拟环境是否存在
echo [检查] 虚拟环境状态...
conda info --envs | findstr /C:"%DEFAULT_ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [创建] 虚拟环境 %DEFAULT_ENV_NAME% 不存在，正在创建...
    conda create -n %DEFAULT_ENV_NAME% python=%DEFAULT_PYTHON_VERSION% -y
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建成功
) else (
    echo [成功] 虚拟环境 %DEFAULT_ENV_NAME% 已存在
)

REM 检查环境配置文件
if not exist ".env" (
    if exist ".env.local.example" (
        echo [配置] 复制环境配置模板...
        copy ".env.local.example" ".env" >nul
        echo [警告] 请编辑 .env 文件并配置API密钥
        echo [警告] 至少需要配置一个API才能正常使用
        echo.
        echo 按任意键继续...
        pause >nul
    ) else (
        echo [警告] 未找到环境配置文件，将使用默认配置
    )
) else (
    echo [成功] 找到环境配置文件
)

REM 创建后端启动脚本
echo [准备] 创建后端启动脚本...
echo @echo off > start_backend_temp.bat
echo echo [后端] 激活conda环境... >> start_backend_temp.bat
echo call conda activate %DEFAULT_ENV_NAME% >> start_backend_temp.bat
echo if errorlevel 1 ^( >> start_backend_temp.bat
echo     echo [错误] 激活环境失败 >> start_backend_temp.bat
echo     pause >> start_backend_temp.bat
echo     exit /b 1 >> start_backend_temp.bat
echo ^) >> start_backend_temp.bat
echo echo [后端] 检查并安装依赖... >> start_backend_temp.bat
echo python -c "import flask" 2^>nul >> start_backend_temp.bat
echo if errorlevel 1 ^( >> start_backend_temp.bat
echo     echo [后端] 安装Python依赖... >> start_backend_temp.bat
echo     pip install -r requirements.txt >> start_backend_temp.bat
echo ^) >> start_backend_temp.bat
echo echo [后端] 启动服务... >> start_backend_temp.bat
echo cd backend >> start_backend_temp.bat
echo set BACKEND_HOST=%BACKEND_HOST% >> start_backend_temp.bat
echo set BACKEND_PORT=%BACKEND_PORT% >> start_backend_temp.bat
echo python app.py >> start_backend_temp.bat

REM 创建前端启动脚本
echo [准备] 创建前端启动脚本...
echo @echo off > start_frontend_temp.bat
echo echo [前端] 激活conda环境... >> start_frontend_temp.bat
echo call conda activate %DEFAULT_ENV_NAME% >> start_frontend_temp.bat
echo if errorlevel 1 ^( >> start_frontend_temp.bat
echo     echo [错误] 激活环境失败 >> start_frontend_temp.bat
echo     pause >> start_frontend_temp.bat
echo     exit /b 1 >> start_frontend_temp.bat
echo ^) >> start_frontend_temp.bat
echo echo [前端] 启动服务... >> start_frontend_temp.bat
echo set BACKEND_HOST=%BACKEND_HOST% >> start_frontend_temp.bat
echo set BACKEND_PORT=%BACKEND_PORT% >> start_frontend_temp.bat
echo set FRONTEND_PORT=%FRONTEND_PORT% >> start_frontend_temp.bat
echo python frontend_server.py >> start_frontend_temp.bat

echo.
echo [启动] 正在启动服务...

REM 启动后端服务
echo [启动] 后端服务 (端口: %BACKEND_PORT%)
start "Long-Novel-GPT 后端" start_backend_temp.bat

REM 等待后端启动
echo [等待] 后端启动中...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo [启动] 前端服务 (端口: %FRONTEND_PORT%)
start "Long-Novel-GPT 前端" start_frontend_temp.bat

REM 等待前端启动
echo [等待] 前端启动中...
timeout /t 8 /nobreak >nul

echo.
echo [完成] 服务启动完成！
echo [访问] 前端地址: http://localhost:%FRONTEND_PORT%
echo [访问] 后端地址: http://localhost:%BACKEND_PORT%
echo [信息] 前端服务将自动打开浏览器
echo.

REM 清理临时文件
timeout /t 2 /nobreak >nul
del start_backend_temp.bat 2>nul
del start_frontend_temp.bat 2>nul

echo [完成] 启动完成，窗口将自动关闭
timeout /t 3 /nobreak >nul