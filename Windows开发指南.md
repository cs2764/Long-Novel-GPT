# Long-Novel-GPT Windows 开发指南

## 概述

本指南专门介绍如何在 Windows 系统中运行 Long-Novel-GPT，无需依赖 Docker。提供了完整的虚拟环境管理和启动脚本。

## 系统要求

### 必需软件
- **Windows 10/11** (支持 PowerShell 5.1+ 或 PowerShell Core 7+)
- **Anaconda/Miniconda**: 用于Python环境管理
- **Git for Windows**: 用于代码管理（可选）

### 推荐配置
- **内存**: 4GB+ RAM
- **存储**: 2GB+ 可用空间
- **网络**: 稳定的互联网连接（用于API调用）

## 快速开始

### 方式1: 使用批处理脚本（推荐新手）

1. **下载并解压项目**
2. **右键以管理员身份运行命令提示符**
3. **切换到项目目录**
   ```cmd
   cd C:\path\to\Long-Novel-GPT
   ```
4. **运行启动脚本**
   ```cmd
   start_local.bat
   ```

脚本会自动：
- 检查并创建conda虚拟环境
- 安装Python依赖
- 配置环境文件
- 启动前后端服务
- 打开浏览器

### 方式2: 使用PowerShell脚本（推荐高级用户）

1. **以管理员身份运行PowerShell**
2. **设置执行策略**（首次使用）
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. **切换到项目目录**
   ```powershell
   cd C:\path\to\Long-Novel-GPT
   ```
4. **运行启动脚本**
   ```powershell
   .\start_local.ps1
   ```

### 方式3: 手动步骤

```cmd
# 1. 创建虚拟环境
conda create -n long-novel-gpt python=3.10 -y

# 2. 激活环境
conda activate long-novel-gpt

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
copy .env.local.example .env
# 编辑 .env 文件

# 5. 启动后端（新命令窗口）
cd backend
python app.py

# 6. 启动前端（另一个新命令窗口）
python frontend_server.py
```

## 虚拟环境管理

### 使用批处理脚本

```cmd
# 创建环境
env_manager.bat create

# 删除环境
env_manager.bat delete

# 查看环境信息
env_manager.bat info

# 列出所有环境
env_manager.bat list

# 清理并重新安装依赖
env_manager.bat clean

# 查看帮助
env_manager.bat help
```

### 使用PowerShell脚本

```powershell
# 创建环境
.\env_manager.ps1 -Command create

# 强制删除环境（不询问确认）
.\env_manager.ps1 -Command delete -Force

# 查看自定义环境信息
.\env_manager.ps1 -Command info -EnvName my-env

# 清理环境
.\env_manager.ps1 -Command clean

# 查看帮助
.\env_manager.ps1 -Command help
```

## 配置说明

### 环境配置文件

复制配置模板：
```cmd
copy .env.local.example .env
```

编辑 `.env` 文件，配置至少一个API：

#### 智谱AI（推荐）
```env
ZHIPUAI_API_KEY=your_api_key_here
ZHIPUAI_AVAILABLE_MODELS=glm-4-air,glm-4-flashx
DEFAULT_MAIN_MODEL=zhipuai/glm-4-air
DEFAULT_SUB_MODEL=zhipuai/glm-4-flashx
```

#### 其他API选项
- **百度文心**: `WENXIN_AK` 和 `WENXIN_SK`
- **字节豆包**: `DOUBAO_API_KEY` 和 `DOUBAO_ENDPOINT_IDS`
- **OpenAI**: `GPT_API_KEY` 和 `GPT_BASE_URL`

### 端口配置

默认端口：
- **前端**: 8080
- **后端**: 7869

自定义端口：
```cmd
set FRONTEND_PORT=8081
set BACKEND_PORT=7870
start_local.bat
```

或PowerShell：
```powershell
.\start_local.ps1 -FrontendPort 8081 -BackendPort 7870
```

## 启动脚本功能对比

| 功能 | 批处理脚本 | PowerShell脚本 |
|------|------------|----------------|
| 自动创建环境 | ✅ | ✅ |
| 依赖检查 | ✅ | ✅ |
| 彩色输出 | ✅ | ✅ |
| 错误处理 | 基础 | 高级 |
| 参数支持 | 有限 | 完整 |
| 后台监控 | ❌ | ✅ |
| 自动浏览器 | ✅ | ✅ |
| 服务管理 | 基础 | 高级 |

## 常见问题解决

### 1. PowerShell执行策略错误

**错误信息**: "因为在此系统上禁止运行脚本"

**解决方案**:
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Conda命令不识别

**错误信息**: "'conda' 不是内部或外部命令"

**解决方案**:
1. 确保已安装Anaconda/Miniconda
2. 重新启动命令提示符/PowerShell
3. 手动添加conda到PATH环境变量

### 3. 端口被占用

**错误信息**: "Address already in use"

**解决方案**:
```cmd
# 查看端口占用
netstat -ano | findstr :8080

# 杀死占用进程
taskkill /PID <进程ID> /F

# 或使用不同端口
set FRONTEND_PORT=8081
start_local.bat
```

### 4. 虚拟环境激活失败

**解决方案**:
```cmd
# 重新初始化conda
conda init cmd.exe

# 或使用完整路径
C:\Users\%USERNAME%\anaconda3\Scripts\activate.bat long-novel-gpt
```

### 5. 依赖安装失败

**解决方案**:
```cmd
# 清理pip缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或使用conda安装主要包
conda install flask flask-cors -c conda-forge
```

## 开发建议

### IDE配置

**VS Code**:
1. 安装Python扩展
2. 选择conda环境作为Python解释器
3. 配置终端使用conda环境

**PyCharm**:
1. 配置项目解释器为conda环境
2. 设置运行配置指向 `backend/app.py`

### 调试模式

后端调试：
```cmd
conda activate long-novel-gpt
cd backend
set FLASK_DEBUG=1
python app.py
```

前端调试：
- 浏览器开发者工具
- 检查API请求到 `/api/*`

### 性能优化

1. **内存使用**:
   ```env
   # 减少线程数
   MAX_THREAD_NUM=2
   ```

2. **启动速度**:
   - 使用SSD存储
   - 关闭不必要的杀毒软件扫描

3. **网络优化**:
   - 配置代理（如果需要）
   - 使用国内API服务

## 脚本文件说明

### 启动脚本
- **`start_local.bat`**: Windows批处理启动脚本
- **`start_local.ps1`**: PowerShell启动脚本，功能更丰富

### 环境管理脚本
- **`env_manager.bat`**: 批处理环境管理脚本
- **`env_manager.ps1`**: PowerShell环境管理脚本

### 核心文件
- **`frontend_server.py`**: 前端开发服务器（支持API代理）
- **`requirements.txt`**: Python依赖列表
- **`.env.local.example`**: 环境配置模板

## 生产部署注意事项

虽然本指南专注于开发环境，但如果要在Windows服务器上部署：

1. **使用IIS作为反向代理**
2. **配置Windows服务运行Python应用**
3. **使用任务计划器自动启动**
4. **配置防火墙规则**
5. **设置日志轮转**

## 故障排除日志

### 启用详细日志

```cmd
# 批处理脚本调试
set DEBUG=1
start_local.bat
```

```powershell
# PowerShell脚本调试
$VerbosePreference = "Continue"
.\start_local.ps1
```

### 常用诊断命令

```cmd
# 检查conda环境
conda info --envs

# 检查Python版本
python --version

# 检查已安装包
pip list

# 测试后端健康
curl http://localhost:7869/health

# 检查端口监听
netstat -ano | findstr :7869
```

## 更新和维护

### 更新依赖
```cmd
conda activate long-novel-gpt
pip install -r requirements.txt --upgrade
```

### 重置环境
```cmd
env_manager.bat clean
```

### 备份配置
定期备份 `.env` 文件和自定义配置。

## 许可证

请参考项目根目录的 LICENSE 文件。