#!/usr/bin/env python3
"""
Long-Novel-GPT 一键启动器
Cross-platform launcher for Long-Novel-GPT
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import socket
import signal
from pathlib import Path

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
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n🛑 收到停止信号 ({signum})，正在关闭服务...")
        self.cleanup()
        sys.exit(0)
    
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
    
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "localhost"
    
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
    
    def run(self):
        """运行启动器"""
        print("=" * 60)
        print("🚀 Long-Novel-GPT 一键启动器")
        print("=" * 60)
        
        # 切换到项目根目录
        os.chdir(self.project_root)
        
        # 检查依赖
        if not self.check_dependencies():
            return 1
        
        print("\n🔧 启动服务...")
        
        # 启动后端
        if not self.start_backend():
            print("❌ 后端启动失败，退出")
            return 1
        
        # 启动前端
        if not self.start_frontend():
            print("❌ 前端启动失败，退出")
            self.cleanup()
            return 1
        
        print(f"\n✅ 所有服务已启动")
        print(f"📡 前端访问地址: http://localhost:{self.frontend_port}")
        print(f"🔗 后端API地址: http://{self.backend_host}:{self.backend_port}")
        print("\n⌨️  按 Ctrl+C 停止所有服务")
        
        try:
            # 等待前端进程结束
            if self.frontend_process:
                self.frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号...")
        finally:
            self.cleanup()
        
        print("✅ 所有服务已停止")
        return 0

def main():
    """主函数"""
    launcher = LongNovelLauncher()
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())