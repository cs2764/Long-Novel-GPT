#!/bin/bash

# Long-Novel-GPT 本地开发启动脚本
# Local development startup script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKEND_PORT=${BACKEND_PORT:-7869}
FRONTEND_PORT=${FRONTEND_PORT:-8080}
BACKEND_HOST=${BACKEND_HOST:-127.0.0.1}

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}Long-Novel-GPT 本地开发环境启动器${NC}"
echo -e "${BLUE}=================================================${NC}"

# 检查conda环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}✗ 请先激活conda虚拟环境${NC}"
    echo -e "${YELLOW}例如: conda activate your_env_name${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 当前conda环境: $CONDA_DEFAULT_ENV${NC}"

# 检查Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Python 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 已安装 ($(python --version))${NC}"

# 检查pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}✗ pip 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip 已安装${NC}"

# 检查环境配置文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠ 未找到.env文件，请复制.env.example为.env并配置相关参数${NC}"
        echo -e "${YELLOW}cp .env.example .env${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠ 未找到.env文件，将使用默认配置${NC}"
    fi
else
    echo -e "${GREEN}✓ 找到.env配置文件${NC}"
fi

# 检查Python依赖
echo -e "${BLUE}🔍 检查Python依赖...${NC}"
if ! python -c "import flask, flask_cors, openai" 2>/dev/null; then
    echo -e "${YELLOW}⚠ 安装Python依赖...${NC}"
    pip install -r requirements.txt
fi

echo -e "${GREEN}✓ 所有Python依赖已安装${NC}"

# 创建启动函数
start_backend() {
    echo -e "${BLUE}🚀 启动后端服务 (端口: $BACKEND_PORT)${NC}"
    cd backend
    export BACKEND_HOST=$BACKEND_HOST
    export BACKEND_PORT=$BACKEND_PORT
    python app.py &
    BACKEND_PID=$!
    cd ..
    echo "后端进程PID: $BACKEND_PID"
}

start_frontend() {
    echo -e "${BLUE}🌐 启动前端服务 (端口: $FRONTEND_PORT)${NC}"
    cd frontend
    
    # 使用Python简单HTTP服务器
    python -m http.server $FRONTEND_PORT &
    FRONTEND_PID=$!
    cd ..
    echo "前端进程PID: $FRONTEND_PID"
}

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}🛑 收到停止信号，正在关闭服务...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ 后端服务已停止${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ 前端服务已停止${NC}"
    fi
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动服务
echo -e "\n${BLUE}🔧 启动服务...${NC}"

start_backend
sleep 3  # 等待后端启动

start_frontend
sleep 2  # 等待前端启动

echo -e "\n${GREEN}🎉 服务启动完成！${NC}"
echo -e "${GREEN}前端地址: http://localhost:$FRONTEND_PORT${NC}"
echo -e "${GREEN}后端地址: http://localhost:$BACKEND_PORT${NC}"
echo -e "\n${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 保持脚本运行
wait