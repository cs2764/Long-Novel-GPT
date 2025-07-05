@echo off 
echo [前端] 激活conda环境... 
call conda activate long-novel-gpt 
if errorlevel 1 ( 
    echo [错误] 激活环境失败 
    pause 
    exit /b 1 
) 
echo [前端] 启动服务... 
set BACKEND_HOST=127.0.0.1 
set BACKEND_PORT=7869 
set FRONTEND_PORT=8080 
python frontend_server.py 
