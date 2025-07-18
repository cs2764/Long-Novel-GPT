# 调试和故障排除指南

本文档提供了Long-Novel-GPT系统的全面调试和故障排除指南，帮助开发者和用户快速解决各种问题。

## 📋 目录

1. [系统架构概述](#系统架构概述)
2. [常见问题排查](#常见问题排查)
3. [日志系统使用](#日志系统使用)
4. [API调试技巧](#API调试技巧)
5. [性能问题分析](#性能问题分析)
6. [配置问题解决](#配置问题解决)
7. [启动问题排查](#启动问题排查)
8. [网络连接问题](#网络连接问题)
9. [数据库问题](#数据库问题)
10. [调试工具使用](#调试工具使用)

## 系统架构概述

### 核心组件

```
Long-Novel-GPT
├── 前端 (Frontend)
│   ├── Web界面 (HTML/CSS/JS)
│   ├── Nginx代理
│   └── 静态资源服务
├── 后端 (Backend)
│   ├── Flask应用
│   ├── API端点
│   ├── 业务逻辑层
│   └── 数据处理
├── 核心引擎 (Core)
│   ├── 动态配置管理
│   ├── 小说生成器
│   ├── 文本处理
│   └── 工具链
└── LLM API层
    ├── 多提供商支持
    ├── 缓存机制
    └── 成本控制
```

### 数据流向

```
用户操作 → 前端界面 → Nginx代理 → Flask后端 → 
核心引擎 → LLM API → 响应处理 → 前端显示
```

## 常见问题排查

### 1. 启动问题

#### 问题：应用无法启动
**症状**：
- 控制台显示错误信息
- 进程无法启动
- 端口被占用

**解决步骤**：
1. 检查端口占用情况
```bash
# Windows
netstat -ano | findstr :7869
netstat -ano | findstr :8099

# Linux/Mac
netstat -tuln | grep :7869
netstat -tuln | grep :8099
```

2. 检查Python环境
```bash
python --version
pip list | grep -E "(flask|gradio|openai)"
```

3. 验证配置文件
```bash
# 检查.env文件是否存在
ls -la .env

# 验证配置格式
python -c "import config; print('配置加载正常')"
```

#### 问题：依赖包缺失
**症状**：
- ModuleNotFoundError
- ImportError

**解决步骤**：
```bash
# 重新安装依赖
pip install -r requirements.txt

# 如果使用conda
conda install --file requirements.txt
```

### 2. API调用问题

#### 问题：API超时
**症状**：
- "timed out"错误
- 请求长时间无响应
- 502 Bad Gateway

**解决步骤**：
1. 检查超时配置
```python
# 查看当前超时设置
grep -r "timeout" config.py
grep -r "proxy_read_timeout" frontend/nginx.conf
```

2. 调整超时时间
```python
# 针对LM Studio本地模型
TIMEOUT = 300  # 5分钟

# 针对云端API
TIMEOUT = 60   # 1分钟
```

3. 验证网络连接
```bash
# 测试API可达性
curl -I https://api.deepseek.com
ping api.deepseek.com
```

#### 问题：API密钥错误
**症状**：
- 401 Unauthorized
- "Invalid API key"
- 认证失败

**解决步骤**：
1. 验证API密钥格式
```python
# 检查密钥长度和格式
api_key = "your-api-key"
print(f"密钥长度: {len(api_key)}")
print(f"密钥格式: {api_key[:20]}...")
```

2. 测试API密钥
```python
import requests
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.deepseek.com/v1/models", headers=headers)
print(response.status_code)
```

### 3. 配置问题

#### 问题：动态配置无法保存
**症状**：
- 配置重启后丢失
- 无法更新配置
- 配置文件格式错误

**解决步骤**：
1. 检查配置文件权限
```bash
ls -la config/
chmod 644 config/*.json
```

2. 验证配置格式
```python
import json
try:
    with open('config/dynamic_config.json', 'r') as f:
        config = json.load(f)
    print("配置格式正确")
except json.JSONDecodeError as e:
    print(f"配置格式错误: {e}")
```

## 日志系统使用

### 1. 日志级别设置

```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 或者通过环境变量
export LOG_LEVEL=DEBUG
```

### 2. 关键日志位置

```bash
# 应用日志
tail -f logs/app.log

# API调用日志
tail -f logs/api.log

# 错误日志
tail -f logs/error.log

# Nginx日志
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log
```

### 3. 日志分析工具

```bash
# 统计错误数量
grep -c "ERROR" logs/app.log

# 查找特定API调用
grep "OpenAI API" logs/api.log

# 分析响应时间
grep "response_time" logs/api.log | awk '{print $NF}' | sort -n
```

## API调试技巧

### 1. 启用详细日志

```python
# 在环境变量中设置
export API_DEBUG=true
export OPENAI_DEBUG=true

# 或在代码中设置
import os
os.environ['API_DEBUG'] = 'true'
```

### 2. 使用curl测试API

```bash
# 测试DeepSeek API
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'

# 测试LM Studio本地API
curl -X GET http://localhost:1234/v1/models
```

### 3. API响应监控

```python
import time
import requests

def monitor_api_response(url, headers, payload):
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_time = time.time() - start_time
        
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response_time:.2f}s")
        print(f"响应大小: {len(response.content)} bytes")
        
        return response
    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.ConnectionError:
        print("连接错误")
```

## 性能问题分析

### 1. 内存使用分析

```python
import psutil
import os

def analyze_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS内存: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS内存: {memory_info.vms / 1024 / 1024:.2f} MB")
    print(f"内存百分比: {process.memory_percent():.2f}%")
```

### 2. CPU使用监控

```python
import psutil
import threading
import time

def monitor_cpu_usage():
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"CPU使用率: {cpu_percent}%")
        time.sleep(5)

# 启动监控线程
monitor_thread = threading.Thread(target=monitor_cpu_usage)
monitor_thread.daemon = True
monitor_thread.start()
```

### 3. 响应时间分析

```python
import time
from collections import defaultdict

response_times = defaultdict(list)

def track_response_time(endpoint, duration):
    response_times[endpoint].append(duration)
    
    # 计算统计信息
    times = response_times[endpoint]
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"{endpoint}: 平均{avg_time:.2f}s, 最大{max_time:.2f}s, 最小{min_time:.2f}s")
```

## 配置问题解决

### 1. 环境变量问题

```bash
# 检查环境变量
env | grep -E "(API_KEY|BASE_URL|MONGODB)"

# 设置环境变量
export DEEPSEEK_API_KEY="your-key-here"
export MONGODB_URI="mongodb://localhost:27017"
```

### 2. 配置文件验证

```python
import os
import json

def validate_config():
    # 检查必要的配置文件
    required_files = ['.env', 'config.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"缺少配置文件: {file}")
            return False
    
    # 验证API密钥
    api_keys = {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ZHIPUAI_API_KEY': os.getenv('ZHIPUAI_API_KEY')
    }
    
    for key, value in api_keys.items():
        if value and len(value) > 10:
            print(f"✅ {key}: 已配置")
        else:
            print(f"❌ {key}: 未配置或格式错误")
    
    return True
```

### 3. 数据库连接问题

```python
from pymongo import MongoClient
import redis

def test_database_connections():
    # 测试MongoDB连接
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB连接正常")
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
    
    # 测试Redis连接
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis连接正常")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
```

## 启动问题排查

### 1. 端口冲突检查

```python
import socket

def check_port_availability(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except OSError:
        return False

# 检查关键端口
ports = [7869, 8099, 1234, 27017, 6379]
for port in ports:
    if check_port_availability(port):
        print(f"✅ 端口 {port} 可用")
    else:
        print(f"❌ 端口 {port} 被占用")
```

### 2. 依赖检查

```python
import importlib
import sys

def check_dependencies():
    required_packages = [
        'flask', 'flask_cors', 'openai', 'requests', 
        'pymongo', 'redis', 'yaml', 'jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 缺失")
    
    if missing_packages:
        print(f"\n请安装缺失的包: pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0
```

### 3. 启动脚本诊断

```bash
#!/bin/bash
# startup_diagnosis.sh

echo "=== 启动诊断开始 ==="

# 检查Python版本
echo "Python版本:"
python --version

# 检查虚拟环境
echo "虚拟环境:"
which python
echo $VIRTUAL_ENV

# 检查配置文件
echo "配置文件:"
ls -la .env config.py

# 检查端口
echo "端口占用情况:"
netstat -tuln | grep -E ":(7869|8099|1234)"

# 检查磁盘空间
echo "磁盘空间:"
df -h .

# 检查内存
echo "内存使用:"
free -h

echo "=== 启动诊断结束 ==="
```

## 网络连接问题

### 1. 代理设置

```python
import os
import requests

# 设置代理
proxies = {
    'http': 'http://proxy.company.com:8080',
    'https': 'http://proxy.company.com:8080',
}

# 测试代理连接
def test_proxy_connection():
    try:
        response = requests.get('https://api.deepseek.com', proxies=proxies, timeout=10)
        print(f"代理连接成功: {response.status_code}")
    except requests.exceptions.ProxyError:
        print("代理连接失败")
    except requests.exceptions.Timeout:
        print("代理连接超时")
```

### 2. 防火墙设置

```bash
# Linux防火墙设置
sudo ufw allow 7869
sudo ufw allow 8099

# Windows防火墙设置
netsh advfirewall firewall add rule name="LongNovelGPT" dir=in action=allow protocol=TCP localport=7869
netsh advfirewall firewall add rule name="LongNovelGPT-Frontend" dir=in action=allow protocol=TCP localport=8099
```

### 3. DNS解析问题

```python
import socket
import dns.resolver

def test_dns_resolution():
    domains = ['api.deepseek.com', 'api.openai.com', 'api.anthropic.com']
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
        except socket.gaierror:
            print(f"❌ {domain} DNS解析失败")
```

## 数据库问题

### 1. MongoDB问题排查

```python
from pymongo import MongoClient
import pymongo.errors

def diagnose_mongodb():
    try:
        client = MongoClient("mongodb://localhost:27017")
        
        # 检查服务器状态
        server_status = client.admin.command('serverStatus')
        print(f"MongoDB版本: {server_status['version']}")
        print(f"运行时间: {server_status['uptime']}秒")
        
        # 检查数据库列表
        databases = client.list_database_names()
        print(f"数据库列表: {databases}")
        
        # 检查集合
        db = client['llm_api']
        collections = db.list_collection_names()
        print(f"集合列表: {collections}")
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ MongoDB服务器连接超时")
    except Exception as e:
        print(f"❌ MongoDB错误: {e}")
```

### 2. 缓存问题

```python
import redis
import json

def diagnose_redis_cache():
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # 检查Redis信息
        info = r.info()
        print(f"Redis版本: {info['redis_version']}")
        print(f"使用内存: {info['used_memory_human']}")
        print(f"键数量: {info['db0']['keys'] if 'db0' in info else 0}")
        
        # 检查缓存键
        cache_keys = r.keys('llm_cache:*')
        print(f"缓存键数量: {len(cache_keys)}")
        
    except redis.ConnectionError:
        print("❌ Redis连接失败")
    except Exception as e:
        print(f"❌ Redis错误: {e}")
```

## 调试工具使用

### 1. 交互式调试

```python
import pdb
import traceback

def debug_function():
    try:
        # 你的代码
        result = some_function()
        return result
    except Exception as e:
        print(f"发生错误: {e}")
        traceback.print_exc()
        pdb.post_mortem()  # 进入调试模式
```

### 2. 日志装饰器

```python
import functools
import logging
import time

def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        logger.info(f"调用函数: {func.__name__}")
        logger.debug(f"参数: args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"函数完成: {func.__name__} (耗时: {execution_time:.2f}s)")
            return result
        except Exception as e:
            logger.error(f"函数异常: {func.__name__} - {str(e)}")
            raise
    
    return wrapper

# 使用示例
@log_function_call
def generate_text(prompt):
    # 你的代码逻辑
    pass
```

### 3. 性能分析器

```python
import cProfile
import pstats

def profile_function(func):
    """性能分析装饰器"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # 生成报告
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # 显示前20个函数
    
    return wrapper
```

### 4. 内存分析

```python
import tracemalloc
import gc

def analyze_memory_leaks():
    # 启动内存跟踪
    tracemalloc.start()
    
    # 执行你的代码
    your_function()
    
    # 获取内存快照
    current, peak = tracemalloc.get_traced_memory()
    print(f"当前内存使用: {current / 1024 / 1024:.2f} MB")
    print(f"峰值内存使用: {peak / 1024 / 1024:.2f} MB")
    
    # 显示内存分配前10位
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    for stat in top_stats[:10]:
        print(stat)
    
    # 手动触发垃圾回收
    gc.collect()
    
    tracemalloc.stop()
```

## 常用调试命令

### 1. 系统信息收集

```bash
# 系统信息
uname -a
python --version
pip --version

# 进程信息
ps aux | grep python
ps aux | grep nginx

# 网络信息
netstat -tuln | grep -E ":(7869|8099|1234|27017|6379)"

# 磁盘信息
df -h
du -sh logs/
```

### 2. 日志分析

```bash
# 实时查看日志
tail -f logs/app.log

# 搜索错误
grep -i error logs/app.log | tail -20

# 统计API调用
grep "API Call" logs/app.log | wc -l

# 分析响应时间
grep "response_time" logs/app.log | awk '{print $NF}' | sort -n | tail -10
```

### 3. 性能监控

```bash
# 系统资源监控
top -p $(pgrep -f "python app.py")

# 内存使用监控
watch -n 1 'ps aux | grep python | grep -v grep'

# 网络监控
netstat -i
ss -tuln
```

## 故障排除清单

### 启动前检查
- [ ] Python版本兼容性
- [ ] 依赖包完整性
- [ ] 配置文件存在性
- [ ] 端口可用性
- [ ] 磁盘空间充足
- [ ] 内存资源充足

### 运行时检查
- [ ] API密钥有效性
- [ ] 网络连接正常
- [ ] 数据库连接正常
- [ ] 缓存系统正常
- [ ] 日志输出正常
- [ ] 错误处理机制

### 性能检查
- [ ] 响应时间合理
- [ ] 内存使用正常
- [ ] CPU使用正常
- [ ] 磁盘I/O正常
- [ ] 网络I/O正常
- [ ] 并发处理正常

## 联系支持

如果以上方法都无法解决问题，请：

1. 收集错误日志
2. 记录重现步骤
3. 提供系统信息
4. 创建GitHub Issue
5. 提供配置文件（去除敏感信息）

---

*本文档会根据系统更新和用户反馈持续完善，如有疑问请查看项目GitHub或提交Issue。* 