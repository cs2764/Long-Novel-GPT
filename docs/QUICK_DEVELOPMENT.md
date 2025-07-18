# 快速开发指南

本文档提供了Long-Novel-GPT项目的快速开发环境搭建指南，帮助开发者快速上手和高效调试。

## 📋 目录

1. [环境准备](#环境准备)
2. [快速启动](#快速启动)
3. [开发环境配置](#开发环境配置)
4. [调试技巧](#调试技巧)
5. [代码结构](#代码结构)
6. [常用开发工具](#常用开发工具)
7. [热重载设置](#热重载设置)
8. [测试流程](#测试流程)
9. [性能优化](#性能优化)
10. [常见问题解决](#常见问题解决)

## 环境准备

### 系统要求

- **Python**: 3.8+
- **Node.js**: 16+ (前端开发需要)
- **内存**: 4GB+
- **磁盘空间**: 2GB+
- **网络**: 稳定的网络连接（用于API调用）

### 必备工具

```bash
# 基础工具
git --version
python --version
pip --version

# 可选工具
docker --version
conda --version
```

## 快速启动

### 1. 项目克隆

```bash
# 克隆项目
git clone https://github.com/your-username/Long-Novel-GPT.git
cd Long-Novel-GPT

# 查看项目结构
tree -L 2 -a
```

### 2. 环境搭建

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置文件设置

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**必要配置项**:
```env
# API配置
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
ZHIPUAI_API_KEY=your-zhipuai-key

# 数据库配置（可选）
MONGODB_URI=mongodb://localhost:27017/
ENABLE_MONGODB=true

# 调试配置
DEBUG=true
LOG_LEVEL=DEBUG
```

### 4. 启动开发服务器

```bash
# 方式1: 使用启动脚本
python launcher.py

# 方式2: 分别启动前后端
# 终端1: 启动后端
python backend/app.py

# 终端2: 启动前端
python frontend_server.py

# 访问应用
open http://localhost:8099
```

## 开发环境配置

### 1. IDE设置

**推荐IDE**: Visual Studio Code

**必备扩展**:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-vscode.vscode-json",
    "bradlc.vscode-tailwindcss"
  ]
}
```

**VS Code配置** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 2. 调试配置

**VS Code调试配置** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Backend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app.py",
      "console": "integratedTerminal",
      "env": {
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
      }
    },
    {
      "name": "Debug Frontend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/frontend_server.py",
      "console": "integratedTerminal"
    }
  ]
}
```

### 3. Git配置

```bash
# 配置Git钩子
cp .githooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# 配置Git忽略
cat >> .gitignore << EOF
# 开发环境
.env
.vscode/
logs/
tmp/
*.log
__pycache__/
*.pyc
.pytest_cache/
EOF
```

## 调试技巧

### 1. 日志调试

```python
import logging

# 配置日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用日志
logger.debug("详细调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 2. 断点调试

```python
import pdb

def debug_function():
    # 设置断点
    pdb.set_trace()
    
    # 你的代码
    result = some_complex_operation()
    
    # 检查变量
    print(f"result: {result}")
    
    return result

# 或者使用装饰器
def debug_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        print(f"参数: {args}, {kwargs}")
        
        result = func(*args, **kwargs)
        
        print(f"返回结果: {result}")
        return result
    
    return wrapper

@debug_decorator
def my_function(x, y):
    return x + y
```

### 3. API调试

```python
# 添加API调试装饰器
from functools import wraps
import time
import json

def api_debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        print(f"=== API调用开始: {func.__name__} ===")
        print(f"参数: {args[:2]}...")  # 只显示前两个参数
        
        try:
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            print(f"=== API调用完成: {execution_time:.2f}s ===")
            
            return result
        except Exception as e:
            print(f"=== API调用异常: {e} ===")
            raise
    
    return wrapper

# 使用示例
@api_debug
def call_openai_api(messages, model):
    # API调用逻辑
    pass
```

### 4. 前端调试

```javascript
// 启用详细日志
window.DEBUG = true;

// 调试函数
function debugLog(message, data) {
    if (window.DEBUG) {
        console.log(`[DEBUG] ${message}`, data);
    }
}

// API调用调试
async function debugApiCall(url, options) {
    debugLog('API请求', { url, options });
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        
        debugLog('API响应', { status: response.status, data });
        
        return data;
    } catch (error) {
        debugLog('API错误', error);
        throw error;
    }
}
```

## 代码结构

### 项目架构

```
Long-Novel-GPT/
├── backend/              # 后端代码
│   ├── app.py           # Flask应用主文件
│   ├── backend_utils.py # 后端工具函数
│   └── requirements.txt # 后端依赖
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── js/              # JavaScript文件
│   └── styles/          # CSS样式
├── core/                # 核心引擎
│   ├── __init__.py
│   ├── writer.py        # 写作引擎
│   ├── dynamic_config_manager.py # 动态配置
│   └── ...
├── llm_api/             # API接口层
│   ├── __init__.py
│   ├── openai_api.py    # OpenAI接口
│   ├── doubao_api.py    # 豆包接口
│   └── ...
├── prompts/             # 提示词模板
│   ├── 创作正文/
│   ├── 创作剧情/
│   └── ...
├── docs/                # 文档
├── tests/               # 测试文件
├── config.py            # 配置文件
└── launcher.py          # 启动器
```

### 核心模块

1. **后端 (Backend)**
   - Flask应用服务器
   - API端点定义
   - 业务逻辑处理

2. **前端 (Frontend)**
   - Web用户界面
   - JavaScript交互逻辑
   - CSS样式设计

3. **核心引擎 (Core)**
   - 小说生成算法
   - 文本处理工具
   - 配置管理系统

4. **API层 (LLM API)**
   - 多提供商API封装
   - 缓存机制
   - 错误处理

## 常用开发工具

### 1. 代码质量工具

```bash
# 安装工具
pip install black flake8 isort pytest

# 代码格式化
black .

# 代码检查
flake8 .

# 导入排序
isort .

# 运行测试
pytest
```

### 2. 开发脚本

创建 `scripts/dev.py`:
```python
#!/usr/bin/env python3
"""开发工具脚本"""

import subprocess
import sys
import os

def run_backend():
    """启动后端开发服务器"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    subprocess.run([sys.executable, 'backend/app.py'])

def run_frontend():
    """启动前端开发服务器"""
    subprocess.run([sys.executable, 'frontend_server.py'])

def run_tests():
    """运行测试"""
    subprocess.run(['pytest', 'tests/', '-v'])

def format_code():
    """格式化代码"""
    subprocess.run(['black', '.'])
    subprocess.run(['isort', '.'])

def lint_code():
    """检查代码质量"""
    subprocess.run(['flake8', '.'])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'backend':
            run_backend()
        elif command == 'frontend':
            run_frontend()
        elif command == 'test':
            run_tests()
        elif command == 'format':
            format_code()
        elif command == 'lint':
            lint_code()
    else:
        print("使用方法: python scripts/dev.py [backend|frontend|test|format|lint]")
```

### 3. 自动化任务

创建 `Makefile`:
```makefile
.PHONY: install dev test format lint clean

# 安装依赖
install:
	pip install -r requirements.txt

# 启动开发环境
dev:
	python launcher.py

# 运行测试
test:
	pytest tests/ -v

# 格式化代码
format:
	black .
	isort .

# 检查代码质量
lint:
	flake8 .

# 清理缓存
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
```

## 热重载设置

### 1. 后端热重载

```python
# backend/app.py 添加热重载
if __name__ == '__main__':
    import os
    
    # 开发环境配置
    if os.getenv('FLASK_ENV') == 'development':
        app.run(
            host='0.0.0.0',
            port=7869,
            debug=True,
            use_reloader=True,  # 启用热重载
            reloader_type='stat'  # 使用stat重载器
        )
    else:
        app.run(host='0.0.0.0', port=7869)
```

### 2. 前端热重载

```python
# frontend_server.py 添加文件监控
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FrontendReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(('.html', '.js', '.css')):
            print(f"文件变更: {event.src_path}")
            # 触发浏览器刷新
            self.notify_clients()
    
    def notify_clients(self):
        # 通过WebSocket通知前端刷新
        pass

def start_file_watcher():
    event_handler = FrontendReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, 'frontend/', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

### 3. 配置文件热重载

```python
# config.py 添加配置热重载
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.env'):
            print("配置文件变更，重新加载...")
            self.reload_config()
    
    def reload_config(self):
        # 重新加载环境变量
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # 通知应用重新加载配置
        self.notify_app_reload()
```

## 测试流程

### 1. 单元测试

```python
# tests/test_writer.py
import pytest
from core.writer import Writer

class TestWriter:
    def test_writer_initialization(self):
        writer = Writer()
        assert writer is not None
    
    def test_text_generation(self):
        writer = Writer()
        result = writer.generate_text("测试提示词")
        assert result is not None
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_async_generation(self):
        writer = Writer()
        result = await writer.async_generate("异步测试")
        assert result is not None
```

### 2. 集成测试

```python
# tests/test_integration.py
import pytest
import requests

class TestIntegration:
    def test_api_endpoint(self):
        response = requests.get('http://localhost:7869/health')
        assert response.status_code == 200
    
    def test_write_endpoint(self):
        data = {
            'writer_mode': 'draft',
            'chunk_list': [['章节1', '内容1']],
            'prompt_content': '测试提示词'
        }
        response = requests.post('http://localhost:7869/write', json=data)
        assert response.status_code == 200
```

### 3. 性能测试

```python
# tests/test_performance.py
import time
import pytest
from core.writer import Writer

class TestPerformance:
    def test_response_time(self):
        writer = Writer()
        
        start_time = time.time()
        result = writer.generate_text("性能测试")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # 响应时间小于5秒
        assert len(result) > 0
    
    def test_memory_usage(self):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行操作
        writer = Writer()
        for i in range(10):
            writer.generate_text(f"测试 {i}")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长不应超过100MB
        assert memory_increase < 100 * 1024 * 1024
```

## 性能优化

### 1. 代码优化

```python
# 使用缓存优化
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(input_data):
    # 耗时操作
    return process_data(input_data)

# 异步处理优化
import asyncio
import aiohttp

async def async_api_call(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

# 批量处理优化
def batch_process(items, batch_size=10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield process_batch(batch)
```

### 2. 数据库优化

```python
# MongoDB连接池
from pymongo import MongoClient
from pymongo.pool import Pool

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(
            'mongodb://localhost:27017/',
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000
        )
        self.db = self.client.llm_api
    
    def get_cached_result(self, key):
        return self.db.cache.find_one({'key': key})
    
    def set_cached_result(self, key, value):
        self.db.cache.update_one(
            {'key': key},
            {'$set': {'value': value, 'timestamp': time.time()}},
            upsert=True
        )
```

### 3. 前端优化

```javascript
// 防抖函数
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// 节流函数
function throttle(func, delay) {
    let lastCall = 0;
    return function (...args) {
        const now = new Date().getTime();
        if (now - lastCall < delay) {
            return;
        }
        lastCall = now;
        return func(...args);
    };
}

// 使用虚拟滚动优化长列表
class VirtualList {
    constructor(container, itemHeight, items) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.items = items;
        this.visibleStart = 0;
        this.visibleEnd = 0;
        this.init();
    }
    
    init() {
        this.container.addEventListener('scroll', 
            throttle(() => this.updateVisibleRange(), 16)
        );
        this.updateVisibleRange();
    }
    
    updateVisibleRange() {
        const scrollTop = this.container.scrollTop;
        const containerHeight = this.container.clientHeight;
        
        this.visibleStart = Math.floor(scrollTop / this.itemHeight);
        this.visibleEnd = Math.min(
            this.visibleStart + Math.ceil(containerHeight / this.itemHeight) + 1,
            this.items.length
        );
        
        this.render();
    }
    
    render() {
        // 只渲染可见范围内的项目
        const visibleItems = this.items.slice(this.visibleStart, this.visibleEnd);
        // 渲染逻辑...
    }
}
```

## 常见问题解决

### 1. 依赖冲突

```bash
# 检查依赖冲突
pip check

# 创建隔离环境
python -m venv clean_env
source clean_env/bin/activate
pip install -r requirements.txt

# 使用requirements.lock固定版本
pip freeze > requirements.lock
```

### 2. 端口占用

```bash
# 查找占用端口的进程
lsof -i :7869
netstat -tuln | grep :7869

# 终止进程
kill -9 <PID>

# 使用不同端口
export BACKEND_PORT=7870
export FRONTEND_PORT=8100
```

### 3. 内存泄漏

```python
# 内存监控
import tracemalloc
import gc

def monitor_memory():
    tracemalloc.start()
    
    # 你的代码
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"当前内存: {current / 1024 / 1024:.2f} MB")
    print(f"峰值内存: {peak / 1024 / 1024:.2f} MB")
    
    # 强制垃圾回收
    gc.collect()
    
    tracemalloc.stop()
```

### 4. API超时

```python
# 配置超时和重试
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    
    # 重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# 使用
session = create_session()
response = session.get(url, timeout=30)
```

## 开发工作流

### 1. 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发代码
# 编写代码...

# 3. 运行测试
make test

# 4. 格式化代码
make format

# 5. 代码检查
make lint

# 6. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 7. 推送分支
git push origin feature/new-feature

# 8. 创建Pull Request
```

### 2. 代码审查

```bash
# 检查列表
- [ ] 代码功能正确
- [ ] 测试用例充足
- [ ] 性能影响可接受
- [ ] 安全性检查通过
- [ ] 文档更新完整
- [ ] 兼容性测试通过
```

### 3. 发布流程

```bash
# 1. 合并到主分支
git checkout main
git merge feature/new-feature

# 2. 更新版本号
python scripts/bump_version.py

# 3. 创建发布标签
git tag -a v1.0.1 -m "Release v1.0.1"

# 4. 推送到远程
git push origin main --tags

# 5. 构建和部署
make build
make deploy
```

## 最佳实践

### 1. 代码风格

- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 编写清晰的注释和文档字符串
- 使用有意义的变量名和函数名

### 2. 错误处理

```python
# 良好的错误处理
import logging

logger = logging.getLogger(__name__)

def safe_api_call(url, data):
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"API调用超时: {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP错误: {e}")
        raise
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise
```

### 3. 性能监控

```python
# 性能监控装饰器
import time
import functools

def monitor_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} 执行时间: {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败: {e} (耗时: {execution_time:.2f}s)")
            raise
    
    return wrapper
```

## 总结

本快速开发指南涵盖了Long-Novel-GPT项目的完整开发环境设置和调试技巧。遵循这些指南可以帮助你：

1. **快速上手**: 按照步骤快速搭建开发环境
2. **高效调试**: 使用各种调试技巧快速定位问题
3. **规范开发**: 遵循最佳实践提高代码质量
4. **性能优化**: 使用监控工具优化系统性能

更多详细信息请参考：
- [调试和故障排除指南](DEBUGGING_GUIDE.md)
- [环境配置指南](ENVIRONMENT_SETUP.md)
- [API配置管理](API_CONFIGURATION.md)

---

*本文档会根据项目发展持续更新，如有疑问请查看项目GitHub或提交Issue。* 