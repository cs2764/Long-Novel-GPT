# Long-Novel-GPT Windows PowerShell 本地开发启动脚本
# Windows PowerShell Local Development Startup Script

param(
    [string]$EnvName = "long-novel-gpt",
    [string]$PythonVersion = "3.10",
    [int]$BackendPort = 7869,
    [int]$FrontendPort = 8080,
    [string]$BackendHost = "127.0.0.1",
    [switch]$Help
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色函数
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# 显示帮助信息
if ($Help) {
    Write-ColorText "Long-Novel-GPT Windows PowerShell 启动脚本" "Cyan"
    Write-ColorText "用法:" "Yellow"
    Write-ColorText "  .\start_local.ps1 [参数]" "White"
    Write-ColorText ""
    Write-ColorText "参数:" "Yellow"
    Write-ColorText "  -EnvName <name>        虚拟环境名称 (默认: long-novel-gpt)" "White"
    Write-ColorText "  -PythonVersion <ver>   Python版本 (默认: 3.10)" "White"
    Write-ColorText "  -BackendPort <port>    后端端口 (默认: 7869)" "White"
    Write-ColorText "  -FrontendPort <port>   前端端口 (默认: 8080)" "White"
    Write-ColorText "  -BackendHost <host>    后端地址 (默认: 127.0.0.1)" "White"
    Write-ColorText "  -Help                  显示此帮助信息" "White"
    Write-ColorText ""
    Write-ColorText "示例:" "Yellow"
    Write-ColorText "  .\start_local.ps1 -FrontendPort 8081 -BackendPort 7870" "White"
    exit 0
}

# 标题
Write-ColorText "==================================================" "Blue"
Write-ColorText "Long-Novel-GPT Windows PowerShell 本地开发环境启动器" "Blue"
Write-ColorText "==================================================" "Blue"
Write-ColorText ""

# 检查执行策略
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-ColorText "✗ PowerShell 执行策略受限" "Red"
    Write-ColorText "请以管理员身份运行以下命令:" "Yellow"
    Write-ColorText "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" "Yellow"
    Read-Host "按回车键退出"
    exit 1
}

# 检查conda是否安装
try {
    $condaVersion = conda --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✓ Conda 已安装: $condaVersion" "Green"
    } else {
        throw "Conda not found"
    }
} catch {
    Write-ColorText "✗ Conda 未安装或未添加到PATH" "Red"
    Write-ColorText "请先安装 Anaconda 或 Miniconda" "Yellow"
    Write-ColorText "下载地址: https://www.anaconda.com/products/distribution" "Yellow"
    Read-Host "按回车键退出"
    exit 1
}

# 检查虚拟环境是否存在
$envExists = $false
try {
    $envList = conda info --envs 2>$null
    if ($envList -match $EnvName) {
        $envExists = $true
        Write-ColorText "✓ 虚拟环境 $EnvName 已存在" "Green"
    }
} catch {
    Write-ColorText "⚠ 无法检查虚拟环境" "Yellow"
}

# 创建虚拟环境（如果不存在）
if (-not $envExists) {
    Write-ColorText "⚠ 虚拟环境 $EnvName 不存在，正在创建..." "Yellow"
    try {
        conda create -n $EnvName python=$PythonVersion -y
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ 虚拟环境创建成功" "Green"
        } else {
            throw "Failed to create environment"
        }
    } catch {
        Write-ColorText "✗ 创建虚拟环境失败" "Red"
        Read-Host "按回车键退出"
        exit 1
    }
}

# 激活虚拟环境
Write-ColorText "🔄 激活虚拟环境..." "Blue"
try {
    conda activate $EnvName
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✓ 虚拟环境已激活: $EnvName" "Green"
    } else {
        throw "Failed to activate environment"
    }
} catch {
    Write-ColorText "✗ 激活虚拟环境失败" "Red"
    Write-ColorText "请手动激活环境: conda activate $EnvName" "Yellow"
    Read-Host "按回车键退出"
    exit 1
}

# 检查环境配置文件
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.local.example") {
        Write-ColorText "⚠ 未找到.env文件，正在复制配置模板..." "Yellow"
        Copy-Item ".env.local.example" ".env"
        Write-ColorText "请编辑 .env 文件并配置相关参数" "Yellow"
        Write-ColorText "至少需要配置一个API才能正常使用" "Yellow"
        Write-ColorText ""
        Read-Host "按回车键继续"
    } else {
        Write-ColorText "⚠ 未找到.env文件，将使用默认配置" "Yellow"
    }
} else {
    Write-ColorText "✓ 找到.env配置文件" "Green"
}

# 检查Python依赖
Write-ColorText "🔍 检查Python依赖..." "Blue"
try {
    python -c "import flask, flask_cors, openai" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✓ 所有Python依赖已安装" "Green"
    } else {
        throw "Dependencies not found"
    }
} catch {
    Write-ColorText "⚠ 安装Python依赖..." "Yellow"
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ 依赖安装成功" "Green"
        } else {
            throw "Failed to install dependencies"
        }
    } catch {
        Write-ColorText "✗ 安装依赖失败" "Red"
        Read-Host "按回车键退出"
        exit 1
    }
}

# 设置环境变量
$env:BACKEND_HOST = $BackendHost
$env:BACKEND_PORT = $BackendPort
$env:FRONTEND_PORT = $FrontendPort

Write-ColorText ""
Write-ColorText "🔧 启动服务..." "Blue"

# 启动后端服务
Write-ColorText "🚀 启动后端服务 (端口: $BackendPort)" "Blue"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    conda activate $using:EnvName
    Set-Location backend
    python app.py
} -Name "BackendService"

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务
Write-ColorText "🌐 启动前端服务 (端口: $FrontendPort)" "Blue"
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    conda activate $using:EnvName
    python frontend_server.py
} -Name "FrontendService"

# 等待前端启动
Start-Sleep -Seconds 2

Write-ColorText ""
Write-ColorText "🎉 服务启动完成！" "Green"
Write-ColorText "前端地址: http://localhost:$FrontendPort" "Green"
Write-ColorText "后端地址: http://localhost:$BackendPort" "Green"
Write-ColorText ""
Write-ColorText "服务正在后台运行..." "Yellow"
Write-ColorText "按 Ctrl+C 停止所有服务" "Yellow"
Write-ColorText ""

# 打开浏览器
Write-ColorText "🌐 正在打开浏览器..." "Blue"
Start-Process "http://localhost:$FrontendPort"

# 监控服务状态
try {
    Write-ColorText "监控服务状态中... (按 Ctrl+C 退出)" "Cyan"
    while ($true) {
        # 检查后端服务状态
        $backendStatus = Get-Job -Name "BackendService" | Select-Object -ExpandProperty State
        $frontendStatus = Get-Job -Name "FrontendService" | Select-Object -ExpandProperty State
        
        if ($backendStatus -eq "Failed" -or $frontendStatus -eq "Failed") {
            Write-ColorText "⚠ 检测到服务异常" "Yellow"
            
            if ($backendStatus -eq "Failed") {
                Write-ColorText "后端服务错误:" "Red"
                Receive-Job -Name "BackendService" -ErrorAction SilentlyContinue
            }
            
            if ($frontendStatus -eq "Failed") {
                Write-ColorText "前端服务错误:" "Red"
                Receive-Job -Name "FrontendService" -ErrorAction SilentlyContinue
            }
            
            break
        }
        
        Start-Sleep -Seconds 5
    }
} catch {
    Write-ColorText "收到停止信号" "Yellow"
} finally {
    # 清理后台任务
    Write-ColorText ""
    Write-ColorText "🛑 正在停止服务..." "Yellow"
    
    Stop-Job -Name "BackendService" -ErrorAction SilentlyContinue
    Stop-Job -Name "FrontendService" -ErrorAction SilentlyContinue
    
    Remove-Job -Name "BackendService" -ErrorAction SilentlyContinue
    Remove-Job -Name "FrontendService" -ErrorAction SilentlyContinue
    
    Write-ColorText "✅ 所有服务已停止" "Green"
}