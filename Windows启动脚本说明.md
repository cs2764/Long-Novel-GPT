# Windows 启动脚本使用说明

## 脚本文件说明

### 启动脚本
1. **`start_local.bat`** - 完整功能版本（推荐）
2. **`start_local_simple.bat`** - 简化版本（故障排除用）
3. **`start_local.ps1`** - PowerShell版本（高级功能）

## 常见问题及解决方案

### 问题1: 脚本创建环境后退出

**原因**: conda环境激活可能导致批处理脚本执行环境改变

**解决方案**:
1. 使用简化版本脚本：
   ```cmd
   start_local_simple.bat
   ```

2. 手动步骤：
   ```cmd
   # 1. 运行环境管理脚本创建环境
   env_manager.bat create
   
   # 2. 手动启动服务
   # 新开命令窗口1:
   conda activate long-novel-gpt
   cd backend
   python app.py
   
   # 新开命令窗口2:
   conda activate long-novel-gpt  
   python frontend_server.py
   ```

### 问题2: 激活环境失败

**可能原因**:
- Conda未正确初始化
- 环境变量问题

**解决方案**:
```cmd
# 1. 初始化conda
conda init cmd.exe

# 2. 重新启动命令提示符

# 3. 重新运行脚本
start_local_simple.bat
```

### 问题3: 依赖安装失败

**解决方案**:
```cmd
# 1. 手动激活环境
conda activate long-novel-gpt

# 2. 手动安装依赖
pip install -r requirements.txt

# 3. 如果仍失败，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 问题4: 端口被占用

**解决方案**:
```cmd
# 查看端口占用
netstat -ano | findstr :8080
netstat -ano | findstr :7869

# 杀死占用进程
taskkill /PID <进程ID> /F

# 或者修改端口
set FRONTEND_PORT=8081
set BACKEND_PORT=7870
start_local_simple.bat
```

## 调试步骤

### 1. 检查conda环境
```cmd
conda info --envs
conda activate long-novel-gpt
python --version
pip list
```

### 2. 检查生成的临时脚本
- `start_backend.bat` - 后端启动脚本
- `start_frontend.bat` - 前端启动脚本

手动运行这些脚本查看详细错误信息。

### 3. 检查依赖
```cmd
conda activate long-novel-gpt
python -c "import flask, flask_cors, openai"
```

### 4. 测试服务
```cmd
# 测试后端
curl http://localhost:7869/health

# 或使用浏览器访问
# http://localhost:7869/health
```

## 推荐使用流程

### 首次使用
1. 运行 `start_local_simple.bat`
2. 如果有问题，查看错误信息
3. 根据错误信息使用上述解决方案

### 日常开发
1. 直接运行 `start_local.bat`
2. 如果遇到问题，切换到 `start_local_simple.bat`

### 高级用户
1. 使用 PowerShell: `.\start_local.ps1`
2. 享受更丰富的功能和更好的错误处理

## 脚本功能对比

| 功能 | start_local.bat | start_local_simple.bat | start_local.ps1 |
|------|-----------------|------------------------|-----------------|
| 自动创建环境 | ✅ | ✅ | ✅ |
| 彩色输出 | ✅ | ❌ | ✅ |
| 错误处理 | 中等 | 基础 | 高级 |
| 调试信息 | 中等 | 详细 | 最详细 |
| 临时脚本 | 保留 | 保留 | 不需要 |
| 兼容性 | 好 | 最好 | 需要PS |

## 常用命令参考

```cmd
# 环境管理
env_manager.bat create    # 创建环境
env_manager.bat delete    # 删除环境
env_manager.bat info      # 查看信息
env_manager.bat clean     # 清理重装

# 手动启动
conda activate long-novel-gpt
cd backend && python app.py                    # 后端
python frontend_server.py                      # 前端

# 检查服务
netstat -ano | findstr :7869                   # 后端端口
netstat -ano | findstr :8080                   # 前端端口
```

## 获取帮助

如果遇到问题，请：
1. 查看本说明文档
2. 查看 `Windows开发指南.md`
3. 使用调试版本脚本获取详细错误信息
4. 手动执行命令进行故障排除