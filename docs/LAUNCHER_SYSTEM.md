# 启动器系统设计文档

## 概述

Long-Novel-GPT 3.0 Enhanced Edition 提供了完整的启动器系统，支持多种启动方式和跨平台兼容性。本文档详细介绍了启动器的架构设计、实现原理和使用方法。

## 系统架构

### 启动器生态系统

```
┌─────────────────────────────────────────────────────────────┐
│                Long-Novel-GPT 启动器系统                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │   Python启动器   │  │  Windows批处理   │  │  Shell脚本  │ │
│  │  (launcher.py)   │  │ (start_local.bat)│  │(.sh/.ps1)   │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
│           │                       │                  │       │
│           ▼                       ▼                  ▼       │
│  ┌─────────────────────────────────────────────────────────┤ │
│  │              核心启动逻辑                                 │ │
│  │  • 环境检查  • 依赖安装  • 端口管理  • 进程控制         │ │
│  └─────────────────────────────────────────────────────────┤ │
│           │                       │                  │       │
│           ▼                       ▼                  ▼       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │    后端服务      │  │    前端服务      │  │  浏览器打开  │ │
│  │  (backend/app.py)│  │(frontend_server) │  │  (自动打开)  │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心启动器设计

### 1. Python启动器 (launcher.py)

**位置：** `launcher.py`

**设计特点：**
- 跨平台兼容性 (Windows, macOS, Linux)
- 自动依赖检查和安装
- 智能端口管理
- 优雅的进程控制
- 自动浏览器打开

**类结构：**
```python
class LongNovelLauncher:
    """Long-Novel-GPT 启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = int(os.environ.get('BACKEND_PORT', 7869))
        self.frontend_port = int(os.environ.get('FRONTEND_PORT', 8099))
        self.backend_host = os.environ.get('BACKEND_HOST', '127.0.0.1')
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
```

### 2. 智能端口管理

**端口检测逻辑：**
```python
def find_free_port(self, start_port):
    """寻找可用的端口"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port

def check_port_available(self, port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False
```

**端口管理流程：**
1. 检查默认端口是否可用
2. 如果被占用，自动寻找可用端口
3. 更新环境变量
4. 显示实际使用的端口

### 3. 依赖检查系统

```python
def check_dependencies(self):
    """检查依赖"""
    print("🔍 检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查必要模块
    required_modules = ['flask', 'flask_cors', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖模块已安装")
    return True
```

### 4. 进程管理

**启动后端服务：**
```python
def start_backend(self):
    """启动后端服务"""
    backend_script = self.project_root / 'backend' / 'app.py'
    
    if not backend_script.exists():
        print("❌ 后端脚本不存在")
        return False
    
    # 检查后端端口
    if not self.check_port_available(self.backend_port):
        print(f"⚠️  后端端口 {self.backend_port} 已被占用，自动寻找可用端口...")
        self.backend_port = self.find_free_port(self.backend_port)
    
    print(f"🚀 启动后端服务 (端口: {self.backend_port})")
    
    # 设置环境变量
    env = os.environ.copy()
    env['BACKEND_PORT'] = str(self.backend_port)
    env['BACKEND_HOST'] = self.backend_host
    
    try:
        self.backend_process = subprocess.Popen(
            [sys.executable, str(backend_script)],
            env=env,
            cwd=str(self.project_root / 'backend'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待后端启动
        print("⏳ 等待后端服务启动...")
        time.sleep(3)
        
        # 检查后端是否启动成功
        if self.backend_process.poll() is None:
            print(f"✅ 后端服务已启动在端口 {self.backend_port}")
            return True
        else:
            stdout, stderr = self.backend_process.communicate()
            print(f"❌ 后端启动失败")
            if stderr:
                print(f"错误信息: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ 启动后端失败: {e}")
        return False
```

**启动前端服务：**
```python
def start_frontend(self):
    """启动前端服务"""
    frontend_script = self.project_root / 'frontend_server.py'
    
    if not frontend_script.exists():
        print("❌ 前端服务器脚本不存在")
        return False
    
    # 检查前端端口
    if not self.check_port_available(self.frontend_port):
        print(f"⚠️  前端端口 {self.frontend_port} 已被占用，自动寻找可用端口...")
        self.frontend_port = self.find_free_port(self.frontend_port)
    
    print(f"🌐 启动前端服务 (端口: {self.frontend_port})")
    print(f"🌍 局域网访问: http://{self.get_local_ip()}:{self.frontend_port}")
    
    # 设置环境变量
    env = os.environ.copy()
    env['FRONTEND_PORT'] = str(self.frontend_port)
    env['BACKEND_PORT'] = str(self.backend_port)
    env['BACKEND_HOST'] = self.backend_host
    
    # 自动打开浏览器
    frontend_url = f"http://localhost:{self.frontend_port}"
    print(f"🔄 准备打开浏览器...")
    self.open_browser(frontend_url)
    
    try:
        self.frontend_process = subprocess.Popen(
            [sys.executable, str(frontend_script)],
            env=env,
            cwd=str(self.project_root)
        )
        return True
        
    except Exception as e:
        print(f"❌ 启动前端失败: {e}")
        return False
```

### 5. 优雅关闭机制

```python
def signal_handler(self, signum, frame):
    """信号处理器"""
    print(f"\n🛑 收到停止信号 ({signum})，正在关闭服务...")
    self.cleanup()
    sys.exit(0)

def cleanup(self):
    """清理进程"""
    print("🧹 清理进程...")
    
    if self.frontend_process:
        try:
            self.frontend_process.terminate()
            self.frontend_process.wait(timeout=5)
            print("✅ 前端服务已停止")
        except:
            self.frontend_process.kill()
            print("⚠️  强制停止前端服务")
    
    if self.backend_process:
        try:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=5)
            print("✅ 后端服务已停止")
        except:
            self.backend_process.kill()
            print("⚠️  强制停止后端服务")
```

## 前端服务器设计

### 1. 前端服务器 (frontend_server.py)

**位置：** `frontend_server.py`

**功能特点：**
- 静态文件服务
- API代理到后端
- 自动端口检测
- 后端健康检查
- 自动浏览器打开

**核心实现：**
```python
class APIProxyHandler(http.server.SimpleHTTPRequestHandler):
    """API代理处理器"""
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(404, "Not Found")
    
    def proxy_to_backend(self):
        """代理请求到后端服务"""
        # 构建后端URL（移除/api前缀）
        backend_path = self.path[4:] if self.path.startswith('/api/') else self.path
        backend_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}{backend_path}"
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # 创建请求
            req = urllib.request.Request(backend_url, data=post_data, method=self.command)
            
            # 复制请求头
            skip_headers = {'host', 'content-length', 'connection'}
            for key, value in self.headers.items():
                if key.lower() not in skip_headers:
                    req.add_header(key, value)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=60) as response:
                # 设置响应状态码
                self.send_response(response.getcode())
                
                # 复制响应头
                skip_response_headers = {'server', 'date', 'transfer-encoding'}
                for key, value in response.headers.items():
                    if key.lower() not in skip_response_headers:
                        self.send_header(key, value)
                
                # 添加CORS头
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                
                self.end_headers()
                
                # 发送响应体
                self.wfile.write(response.read())
                
        except Exception as e:
            print(f"代理请求失败: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
```

### 2. 后端健康检查

```python
def check_backend_status():
    """检查后端服务状态"""
    try:
        response = urllib.request.urlopen(f"http://{BACKEND_HOST}:{BACKEND_PORT}/health", timeout=5)
        return response.getcode() == 200
    except:
        return False
```

## Windows启动脚本

### 1. 批处理脚本 (start_local.bat)

**特点：**
- 自动创建conda环境
- 智能依赖检查
- 并行启动服务
- 自动浏览器打开

**核心逻辑：**
```batch
@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM 配置
set DEFAULT_ENV_NAME=long-novel-gpt
set DEFAULT_PYTHON_VERSION=3.10
set BACKEND_PORT=7869
set FRONTEND_PORT=8080

REM 检查conda环境
conda info --envs | findstr /C:"%DEFAULT_ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [创建] 虚拟环境 %DEFAULT_ENV_NAME% 不存在，正在创建...
    conda create -n %DEFAULT_ENV_NAME% python=%DEFAULT_PYTHON_VERSION% -y
)

REM 激活环境并启动服务
call conda activate %DEFAULT_ENV_NAME%
start "后端服务" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul
start "前端服务" cmd /k "python frontend_server.py"
```

### 2. PowerShell脚本 (start_local.ps1)

**特点：**
- 彩色输出
- 详细状态显示
- 错误处理
- 后台作业管理

**核心功能：**
```powershell
# 启动后端服务
Write-ColorText "🚀 启动后端服务 (端口: $BackendPort)" "Blue"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    conda activate $using:EnvName
    Set-Location backend
    python app.py
} -Name "BackendService"

# 启动前端服务
Write-ColorText "🌐 启动前端服务 (端口: $FrontendPort)" "Blue"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    conda activate $using:EnvName
    python frontend_server.py
} -Name "FrontendService"

# 打开浏览器
Write-ColorText "🌐 正在打开浏览器..." "Blue"
Start-Process "http://localhost:$FrontendPort"
```

## 自动浏览器打开

### 1. 延迟打开机制

```python
def open_browser(self, url, delay=3):
    """延迟打开浏览器"""
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"✅ 浏览器已自动打开: {url}")
        except Exception as e:
            print(f"❌ 打开浏览器失败: {e}")
            print(f"请手动访问: {url}")
    
    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()
```

### 2. 跨平台兼容性

```python
def get_local_ip(self):
    """获取本机IP地址"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"
```

## 启动方式对比

| 启动方式 | 平台支持 | 依赖管理 | 自动化程度 | 适用场景 |
|----------|----------|----------|------------|----------|
| **launcher.py** | 全平台 | 自动检查 | 高 | 生产环境 |
| **frontend_server.py** | 全平台 | 需手动 | 中 | 前端开发 |
| **start_local.bat** | Windows | 自动创建 | 高 | Windows用户 |
| **start_local.ps1** | Windows | 自动创建 | 高 | 高级用户 |
| **start_local.sh** | Unix/Linux | 自动检查 | 高 | Linux/macOS |

## 配置管理

### 1. 环境变量配置

```bash
# 端口配置
export FRONTEND_PORT=8099
export BACKEND_PORT=7869
export BACKEND_HOST=127.0.0.1

# 开发模式
export DEBUG=1
export FLASK_ENV=development
```

### 2. 配置文件

**Windows配置文件：**
```ini
[DEFAULT]
FRONTEND_PORT=8099
BACKEND_PORT=7869
BACKEND_HOST=127.0.0.1
ENV_NAME=long-novel-gpt
PYTHON_VERSION=3.10
```

**Unix配置文件：**
```bash
#!/bin/bash
export FRONTEND_PORT=8099
export BACKEND_PORT=7869
export BACKEND_HOST=127.0.0.1
```

## 监控和日志

### 1. 服务状态监控

```python
def monitor_services(self):
    """监控服务状态"""
    while True:
        try:
            # 检查后端状态
            backend_status = self.check_backend_status()
            
            # 检查前端状态
            frontend_status = self.frontend_process and self.frontend_process.poll() is None
            
            if not backend_status:
                print("⚠️  后端服务异常，尝试重启...")
                self.restart_backend()
            
            if not frontend_status:
                print("⚠️  前端服务异常，尝试重启...")
                self.restart_frontend()
            
            time.sleep(30)  # 每30秒检查一次
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"监控异常: {e}")
            time.sleep(10)
```

### 2. 日志系统

```python
import logging
from datetime import datetime

def setup_logging():
    """设置日志系统"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    
    # 文件日志
    file_handler = logging.FileHandler('launcher.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    
    # 根日志器
    logger = logging.getLogger('launcher')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

## 故障排除

### 1. 常见问题

**问题1：端口被占用**
```bash
# 查看端口占用
netstat -ano | findstr :8099  # Windows
lsof -i :8099                 # macOS/Linux

# 自动解决
# 启动器会自动寻找可用端口
```

**问题2：依赖缺失**
```bash
# 检查依赖
pip list | grep flask

# 自动安装
pip install -r requirements.txt
```

**问题3：权限问题**
```bash
# Windows
# 以管理员身份运行PowerShell

# macOS/Linux
chmod +x start_local.sh
```

### 2. 调试模式

```python
# 启用调试模式
export DEBUG=1
python launcher.py

# 详细日志
export LAUNCHER_DEBUG=1
python launcher.py
```

### 3. 手动启动验证

```bash
# 手动启动后端
cd backend
python app.py

# 手动启动前端
python frontend_server.py

# 验证服务
curl http://localhost:7869/health
curl http://localhost:8099/
```

## 性能优化

### 1. 启动速度优化

- **并行启动**：同时启动前后端服务
- **懒加载**：仅在需要时加载模块
- **缓存检查**：避免重复的依赖检查

### 2. 资源管理

- **进程监控**：监控子进程状态
- **内存管理**：及时清理无用对象
- **连接池**：复用网络连接

### 3. 错误恢复

```python
def auto_restart_service(self, service_name, max_retries=3):
    """自动重启服务"""
    for attempt in range(max_retries):
        try:
            if service_name == "backend":
                success = self.start_backend()
            elif service_name == "frontend":
                success = self.start_frontend()
            
            if success:
                print(f"✅ {service_name} 重启成功")
                return True
            else:
                print(f"❌ {service_name} 重启失败，尝试 {attempt + 1}/{max_retries}")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ {service_name} 重启异常: {e}")
            time.sleep(5)
    
    print(f"❌ {service_name} 重启失败，已达到最大重试次数")
    return False
```

## 扩展指南

### 1. 添加新的启动方式

```python
class DockerLauncher(LongNovelLauncher):
    """Docker启动器"""
    
    def start_backend(self):
        """使用Docker启动后端"""
        try:
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'lngpt-backend',
                '-p', f'{self.backend_port}:7869',
                'lngpt-backend:latest'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def start_frontend(self):
        """使用Docker启动前端"""
        try:
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'lngpt-frontend',
                '-p', f'{self.frontend_port}:8099',
                'lngpt-frontend:latest'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
```

### 2. 自定义配置选项

```python
class CustomLauncher(LongNovelLauncher):
    """自定义启动器"""
    
    def __init__(self, config_file=None):
        super().__init__()
        self.config_file = config_file or "launcher_config.json"
        self.load_custom_config()
    
    def load_custom_config(self):
        """加载自定义配置"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.backend_port = config.get('backend_port', self.backend_port)
            self.frontend_port = config.get('frontend_port', self.frontend_port)
            self.auto_open_browser = config.get('auto_open_browser', True)
            
        except FileNotFoundError:
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'backend_port': 7869,
            'frontend_port': 8099,
            'auto_open_browser': True,
            'backend_host': '127.0.0.1'
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
```

## 最佳实践

### 1. 开发环境

- 使用 `launcher.py` 进行一键启动
- 配置IDE集成，直接从IDE启动
- 使用调试模式获取详细日志

### 2. 生产环境

- 使用系统服务管理器 (systemd, Windows Service)
- 配置自动重启机制
- 监控服务状态和性能

### 3. 测试环境

- 使用Docker容器进行隔离
- 配置CI/CD自动化部署
- 进行负载测试和压力测试

## 总结

启动器系统为Long-Novel-GPT提供了完整的启动解决方案，具有以下特点：

- **跨平台兼容**：支持Windows、macOS、Linux
- **智能化管理**：自动端口检测、依赖检查、错误恢复
- **多种启动方式**：Python脚本、批处理、Shell脚本
- **优雅的进程控制**：信号处理、资源清理
- **用户友好**：自动浏览器打开、详细状态显示
- **可扩展性**：易于添加新功能和自定义配置

这个系统大大简化了应用的部署和运行，提供了良好的用户体验。 