@echo off 
echo [后端] 激活conda环境... 
call conda activate long-novel-gpt 
if errorlevel 1 ( 
    echo [错误] 激活环境失败 
    pause 
    exit /b 1 
) 
echo [后端] 检查并安装依赖... 
python -c "import flask" 2>nul 
if errorlevel 1 ( 
    echo [后端] 安装Python依赖... 
    pip install -r requirements.txt 
) 
echo [后端] 启动服务... 
cd backend 
set BACKEND_HOST=127.0.0.1 
set BACKEND_PORT=7869 
python app.py 
