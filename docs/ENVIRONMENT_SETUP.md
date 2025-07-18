# 环境配置指南

## 概述

本文档提供了Long-Novel-GPT的完整环境配置指南，包括系统要求、依赖安装、配置文件设置等详细步骤。

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 | 说明 |
|------|----------|----------|------|
| **CPU** | 双核 2.0GHz | 四核 3.0GHz+ | 影响处理速度 |
| **内存** | 4GB RAM | 8GB+ RAM | 影响并发处理能力 |
| **存储** | 2GB 可用空间 | 10GB+ SSD | 存储代码、日志、缓存 |
| **网络** | 稳定网络连接 | 高速网络 | API调用需要 |

### 软件要求

| 软件 | 版本要求 | 必需/可选 | 说明 |
|------|----------|-----------|------|
| **Python** | 3.8+ | 必需 | 推荐 3.10+ |
| **Git** | 2.0+ | 推荐 | 代码管理 |
| **Node.js** | 16+ | 可选 | 前端开发 |
| **MongoDB** | 4.4+ | 可选 | 日志存储 |
| **Redis** | 6.0+ | 可选 | 缓存服务 |

### 操作系统支持

| 系统 | 支持状态 | 说明 |
|------|----------|------|
| **Windows** | ✅ 完全支持 | 10/11，提供专用脚本 |
| **macOS** | ✅ 完全支持 | 10.15+ |
| **Linux** | ✅ 完全支持 | Ubuntu 18.04+, CentOS 7+ |

## 环境管理

### 1. Conda环境管理（推荐）

**安装Conda：**
```bash
# 下载Miniconda
# Windows: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
# macOS: https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
# Linux: https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Linux/macOS 安装
bash Miniconda3-latest-Linux-x86_64.sh

# 重启终端或执行
source ~/.bashrc
```

**创建虚拟环境：**
```bash
# 创建环境
conda create -n long-novel-gpt python=3.10 -y

# 激活环境
conda activate long-novel-gpt

# 验证环境
python --version
which python
```

### 2. venv环境管理（替代方案）

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 验证环境
python --version
```

### 3. pyenv版本管理（高级用户）

```bash
# 安装pyenv
curl https://pyenv.run | bash

# 重启终端后安装Python
pyenv install 3.10.12
pyenv global 3.10.12

# 验证
python --version
```

## 项目安装

### 1. 获取代码

```bash
# 克隆项目
git clone https://github.com/your-org/Long-Novel-GPT.git
cd Long-Novel-GPT

# 检查分支
git branch -a
git checkout dev  # 如果需要切换到开发分支
```

### 2. 安装依赖

**基础依赖：**
```bash
# 激活环境
conda activate long-novel-gpt

# 安装依赖
pip install -r requirements.txt

# 验证安装
pip list | grep flask
pip list | grep requests
```

**可选依赖：**
```bash
# 开发依赖
pip install -r requirements-dev.txt

# 测试依赖
pip install pytest pytest-cov

# 文档依赖
pip install sphinx sphinx-rtd-theme
```

### 3. 验证安装

```bash
# 检查Python环境
python -c "import sys; print(sys.version)"
python -c "import flask; print('Flask OK')"
python -c "import requests; print('Requests OK')"

# 检查项目结构
ls -la
ls backend/
ls frontend/
```

## 配置文件设置

### 1. 环境变量配置

**创建 `.env` 文件：**
```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env  # 或使用其他编辑器
```

**`.env` 文件示例：**
```env
# === API 配置 ===
# DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1

# 智谱AI API
ZHIPUAI_API_KEY=your-zhipuai-api-key
ZHIPUAI_MODEL=glm-4-air

# === 服务配置 ===
BACKEND_HOST=127.0.0.1
BACKEND_PORT=7869
FRONTEND_PORT=8099

# === 功能配置 ===
MAX_THREAD_NUM=5
MAX_NOVEL_SUMMARY_LENGTH=20000

# === MongoDB 配置 ===
ENABLE_MONGODB=false
MONGODB_URI=mongodb://127.0.0.1:27017/
MONGODB_DB_NAME=llm_api
ENABLE_MONGODB_CACHE=true

# === 费用限制 ===
API_HOURLY_LIMIT_RMB=100
API_DAILY_LIMIT_RMB=500
API_USD_TO_RMB_RATE=7

# === 日志配置 ===
LOG_LEVEL=INFO
LOG_FILE=app.log
ENABLE_MONGODB_LOGGING=false
```

### 2. 动态配置

**创建运行时配置：**
```bash
# 复制模板
cp backend/runtime_config.json.example runtime_config.json

# 编辑配置
nano runtime_config.json
```

**`runtime_config.json` 示例：**
```json
{
  "current_provider": "deepseek",
  "providers": {
    "deepseek": {
      "name": "deepseek",
      "api_key": "sk-your-api-key",
      "model_name": "deepseek-chat",
      "base_url": "https://api.deepseek.com/v1",
      "models": ["deepseek-chat", "deepseek-coder"],
      "system_prompt": ""
    },
    "zhipuai": {
      "name": "zhipuai",
      "api_key": "your-zhipuai-key",
      "model_name": "glm-4-air",
      "base_url": null,
      "models": ["glm-4-air", "glm-4-flashx"],
      "system_prompt": ""
    }
  }
}
```

### 3. 配置验证

```bash
# 验证配置文件
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('环境变量加载成功')
print(f'BACKEND_PORT: {os.getenv(\"BACKEND_PORT\")}')
print(f'FRONTEND_PORT: {os.getenv(\"FRONTEND_PORT\")}')
"

# 验证API密钥
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key and not api_key.startswith('sk-'):
    print('⚠️  API密钥格式可能不正确')
else:
    print('✅ API密钥格式正确')
"
```

## 数据库配置

### 1. MongoDB配置（可选）

**安装MongoDB：**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# CentOS/RHEL
sudo yum install mongodb

# macOS
brew install mongodb-community

# Windows
# 下载安装包: https://www.mongodb.com/try/download/community
```

**启动MongoDB：**
```bash
# Linux/macOS
sudo systemctl start mongod
# 或
mongod --dbpath /data/db

# Windows
net start MongoDB
```

**配置MongoDB：**
```bash
# 进入MongoDB shell
mongo

# 创建数据库
use llm_api

# 创建用户（可选）
db.createUser({
  user: "lngpt",
  pwd: "your-password",
  roles: ["readWrite"]
})
```

### 2. Redis配置（可选）

**安装Redis：**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# CentOS/RHEL
sudo yum install redis

# macOS
brew install redis

# Windows
# 下载: https://github.com/microsoftarchive/redis/releases
```

**启动Redis：**
```bash
# Linux/macOS
sudo systemctl start redis
# 或
redis-server

# Windows
redis-server.exe
```

**测试Redis：**
```bash
# 测试连接
redis-cli ping
# 期望输出: PONG
```

## 网络配置

### 1. 端口配置

**检查端口占用：**
```bash
# Linux/macOS
lsof -i :7869
lsof -i :8099

# Windows
netstat -ano | findstr :7869
netstat -ano | findstr :8099
```

**配置防火墙：**
```bash
# Ubuntu/Debian
sudo ufw allow 7869
sudo ufw allow 8099

# CentOS/RHEL
sudo firewall-cmd --add-port=7869/tcp --permanent
sudo firewall-cmd --add-port=8099/tcp --permanent
sudo firewall-cmd --reload

# macOS
# 系统偏好设置 > 安全性与隐私 > 防火墙
```

### 2. 代理配置

**HTTP代理：**
```bash
# 临时设置
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080

# 永久设置 (添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export HTTP_PROXY=http://proxy.example.com:8080' >> ~/.bashrc
echo 'export HTTPS_PROXY=https://proxy.example.com:8080' >> ~/.bashrc
```

**在Python中使用代理：**
```python
import os
import requests

proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
}

response = requests.get('https://api.example.com', proxies=proxies)
```

## SSL/TLS配置

### 1. 自签名证书

**生成证书：**
```bash
# 生成私钥
openssl genrsa -out server.key 2048

# 生成证书签名请求
openssl req -new -key server.key -out server.csr

# 生成自签名证书
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# 合并证书和私钥
cat server.crt server.key > server.pem
```

**配置HTTPS：**
```python
# 在Flask应用中启用HTTPS
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=('server.crt', 'server.key'),
        debug=False
    )
```

### 2. Let's Encrypt证书

**安装Certbot：**
```bash
# Ubuntu/Debian
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot
```

**获取证书：**
```bash
# 为域名获取证书
sudo certbot certonly --standalone -d your-domain.com

# 证书路径
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

## 性能优化

### 1. Python优化

**使用更快的JSON库：**
```bash
pip install orjson
```

```python
# 替换标准json库
import orjson as json

# 使用
data = json.loads(json_string)
json_string = json.dumps(data)
```

**使用更快的HTTP客户端：**
```bash
pip install httpx
```

```python
import httpx

async def async_request():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com')
        return response.json()
```

### 2. 数据库优化

**MongoDB索引：**
```javascript
// 在MongoDB中创建索引
db.api_cost.createIndex({"created_at": 1})
db.api_cost.createIndex({"model": 1, "created_at": 1})
db.stream_chat.createIndex({"cache_key": 1})
```

**Redis优化：**
```bash
# 修改Redis配置
# /etc/redis/redis.conf

# 增加最大内存
maxmemory 256mb

# 设置内存策略
maxmemory-policy allkeys-lru
```

### 3. 系统优化

**增加文件描述符限制：**
```bash
# 临时增加
ulimit -n 10000

# 永久设置
echo "* soft nofile 10000" >> /etc/security/limits.conf
echo "* hard nofile 10000" >> /etc/security/limits.conf
```

**优化网络设置：**
```bash
# 增加TCP连接数
echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 1024" >> /etc/sysctl.conf
sysctl -p
```

## 安全配置

### 1. API密钥管理

**使用环境变量：**
```bash
# 设置环境变量
export DEEPSEEK_API_KEY="sk-your-key-here"

# 在代码中使用
import os
api_key = os.getenv('DEEPSEEK_API_KEY')
```

**使用密钥文件：**
```bash
# 创建密钥文件
echo "sk-your-key-here" > ~/.deepseek_key
chmod 600 ~/.deepseek_key

# 在代码中读取
with open(os.path.expanduser('~/.deepseek_key')) as f:
    api_key = f.read().strip()
```

### 2. 访问控制

**IP白名单：**
```python
ALLOWED_IPS = ['127.0.0.1', '192.168.1.0/24']

def check_ip(request):
    client_ip = request.remote_addr
    return client_ip in ALLOWED_IPS
```

**API限流：**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chat')
@limiter.limit("10 per minute")
def chat():
    return process_chat()
```

### 3. 数据加密

**配置文件加密：**
```python
from cryptography.fernet import Fernet

# 生成密钥
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 加密配置
encrypted_config = cipher_suite.encrypt(config_data.encode())

# 解密配置
decrypted_config = cipher_suite.decrypt(encrypted_config).decode()
```

## 监控配置

### 1. 日志监控

**配置日志轮转：**
```python
import logging.handlers

# 配置轮转文件处理器
handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# 配置时间轮转
handler = logging.handlers.TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=7
)
```

### 2. 性能监控

**系统监控：**
```bash
# 安装系统监控工具
pip install psutil

# 监控脚本
python -c "
import psutil
print(f'CPU使用率: {psutil.cpu_percent()}%')
print(f'内存使用率: {psutil.virtual_memory().percent}%')
print(f'磁盘使用率: {psutil.disk_usage(\"/\").percent}%')
"
```

**应用监控：**
```python
import time
import psutil
import threading

class SystemMonitor:
    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def _monitor_loop(self):
        while self.running:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                print(f"⚠️  CPU使用率过高: {cpu_percent}%")
            
            if memory_percent > 80:
                print(f"⚠️  内存使用率过高: {memory_percent}%")
            
            time.sleep(60)  # 每分钟检查一次
    
    def stop(self):
        self.running = False
```

## 故障排除

### 1. 常见问题

**Python模块导入错误：**
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 检查虚拟环境
which python
conda info --envs

# 重新安装依赖
pip install --upgrade -r requirements.txt
```

**端口被占用：**
```bash
# 查找占用进程
lsof -i :7869
netstat -ano | findstr :7869

# 终止进程
kill -9 <PID>
# Windows
taskkill /PID <PID> /F
```

**权限问题：**
```bash
# 检查文件权限
ls -la

# 修改权限
chmod 755 start_local.sh
chown user:group config.py
```

### 2. 调试技巧

**启用调试模式：**
```bash
export DEBUG=1
export FLASK_ENV=development
python app.py
```

**检查配置加载：**
```python
# 验证配置
python -c "
import os
import json
from dotenv import load_dotenv

load_dotenv()
print('环境变量:')
for key, value in os.environ.items():
    if 'API_KEY' in key:
        print(f'{key}: {value[:10]}...')
    elif key.startswith('BACKEND_') or key.startswith('FRONTEND_'):
        print(f'{key}: {value}')
"
```

**测试网络连接：**
```python
import requests
import os

# 测试API连接
def test_api_connection():
    try:
        response = requests.get('https://api.deepseek.com', timeout=10)
        print(f"✅ API连接正常: {response.status_code}")
    except Exception as e:
        print(f"❌ API连接失败: {e}")

test_api_connection()
```

## 部署检查清单

### 1. 环境检查

- [ ] Python 3.8+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖包已安装
- [ ] 配置文件已创建并设置
- [ ] API密钥已配置
- [ ] 端口未被占用
- [ ] 防火墙规则已配置

### 2. 功能检查

- [ ] 后端服务可以启动
- [ ] 前端服务可以启动
- [ ] API调用正常
- [ ] 数据库连接正常（如果使用）
- [ ] 日志记录正常
- [ ] 缓存功能正常（如果启用）

### 3. 性能检查

- [ ] 响应时间在可接受范围内
- [ ] 内存使用量正常
- [ ] CPU使用率正常
- [ ] 磁盘空间充足
- [ ] 网络连接稳定

### 4. 安全检查

- [ ] API密钥安全存储
- [ ] 访问控制配置正确
- [ ] SSL/TLS配置正确（如果使用）
- [ ] 敏感文件权限正确
- [ ] 日志不包含敏感信息

## 总结

通过本指南，您应该能够：

1. **准备环境**：选择合适的操作系统和安装必要的软件
2. **配置项目**：正确设置配置文件和环境变量
3. **安装依赖**：使用conda或pip安装所有必需的包
4. **配置数据库**：设置MongoDB和Redis（如果需要）
5. **优化性能**：根据需求调整系统和应用参数
6. **确保安全**：正确配置访问控制和加密
7. **监控系统**：设置日志和性能监控

正确的环境配置是Long-Novel-GPT稳定运行的基础，请按照本指南逐步完成配置。 