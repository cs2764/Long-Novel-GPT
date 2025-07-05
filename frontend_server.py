#!/usr/bin/env python3
"""
前端开发服务器，支持API代理到后端
Frontend development server with API proxy support
"""

import os
import sys
import http.server
import socketserver
import urllib.request
import urllib.parse
import webbrowser
import threading
import time
import socket
from pathlib import Path

# 配置
FRONTEND_PORT = int(os.environ.get('FRONTEND_PORT', 8099))
BACKEND_PORT = int(os.environ.get('BACKEND_PORT', 7869))
BACKEND_HOST = os.environ.get('BACKEND_HOST', '127.0.0.1').strip()

class APIProxyHandler(http.server.SimpleHTTPRequestHandler):
    """支持API代理的HTTP请求处理器"""
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        if self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
        else:
            super().do_OPTIONS()
    
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
            
            # 复制请求头（排除一些不需要的头）
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
                
        except urllib.error.HTTPError as e:
            # HTTP错误
            self.send_response(e.code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(e.read())
            
        except Exception as e:
            # 其他错误
            print(f"代理请求失败: {e}")
            self.send_error(502, f"Bad Gateway: {e}")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")

def find_free_port(start_port=8099):
    """寻找可用的端口"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port

def open_browser(url, delay=2):
    """延迟打开浏览器"""
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"✅ 浏览器已打开: {url}")
        except Exception as e:
            print(f"❌ 打开浏览器失败: {e}")
            print(f"请手动访问: {url}")
    
    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()

def check_backend_status():
    """检查后端服务状态"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((BACKEND_HOST, BACKEND_PORT))
            return result == 0
    except:
        return False

def main():
    """主函数"""
    global FRONTEND_PORT
    
    # 切换到frontend目录
    frontend_dir = Path(__file__).parent / 'frontend'
    if not frontend_dir.exists():
        print("❌ 错误: frontend目录不存在")
        return 1
    
    os.chdir(frontend_dir)
    
    # 检查并自动寻找可用端口
    if FRONTEND_PORT != 8099:  # 如果环境变量指定了端口，先尝试使用
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', FRONTEND_PORT))
        except OSError:
            print(f"⚠️  端口 {FRONTEND_PORT} 已被占用，自动寻找可用端口...")
            FRONTEND_PORT = find_free_port(FRONTEND_PORT)
    else:
        # 使用默认端口查找逻辑
        FRONTEND_PORT = find_free_port(FRONTEND_PORT)
    
    # 检查后端服务状态
    backend_status = check_backend_status()
    backend_status_text = "✅ 运行中" if backend_status else "❌ 未启动"
    
    print("=" * 60)
    print("🚀 Long-Novel-GPT 前端服务器启动中...")
    print("=" * 60)
    print(f"📡 前端端口: {FRONTEND_PORT}")
    print(f"🔗 后端代理: http://{BACKEND_HOST}:{BACKEND_PORT} ({backend_status_text})")
    print(f"🌐 访问地址: http://localhost:{FRONTEND_PORT}")
    print(f"🌍 局域网访问: http://{get_local_ip()}:{FRONTEND_PORT}")
    
    if not backend_status:
        print("\n⚠️  警告: 后端服务未启动，请先启动后端服务")
        print("   启动命令: python backend/app.py")
    
    print("\n⌨️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 自动打开浏览器
    frontend_url = f"http://localhost:{FRONTEND_PORT}"
    print(f"🔄 准备打开浏览器...")
    open_browser(frontend_url)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", FRONTEND_PORT), APIProxyHandler) as httpd:
            print(f"✅ 前端服务器已启动在端口 {FRONTEND_PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
        print("✅ 前端服务器已停止")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {FRONTEND_PORT} 已被占用")
            print("请检查是否有其他进程占用该端口，或使用环境变量指定其他端口:")
            print(f"FRONTEND_PORT=8100 python frontend_server.py")
        else:
            print(f"❌ 启动服务器失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return 1
    
    return 0

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

if __name__ == "__main__":
    sys.exit(main())