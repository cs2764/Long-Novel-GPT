# Long-Novel-GPT Windows PowerShell 虚拟环境管理脚本
# Windows PowerShell Virtual Environment Management Script

param(
    [string]$Command = "help",
    [string]$EnvName = "long-novel-gpt",
    [string]$PythonVersion = "3.10",
    [switch]$Force
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
function Show-Help {
    Write-ColorText "Long-Novel-GPT 虚拟环境管理器" "Cyan"
    Write-ColorText "=====================================" "Cyan"
    Write-ColorText ""
    Write-ColorText "用法:" "Yellow"
    Write-ColorText "  .\env_manager.ps1 -Command <command> [参数]" "White"
    Write-ColorText ""
    Write-ColorText "命令:" "Yellow"
    Write-ColorText "  create    - 创建虚拟环境" "White"
    Write-ColorText "  delete    - 删除虚拟环境" "White"
    Write-ColorText "  activate  - 激活虚拟环境" "White"
    Write-ColorText "  info      - 显示环境信息" "White"
    Write-ColorText "  list      - 列出所有环境" "White"
    Write-ColorText "  clean     - 清理所有依赖并重新安装" "White"
    Write-ColorText "  help      - 显示此帮助信息" "White"
    Write-ColorText ""
    Write-ColorText "参数:" "Yellow"
    Write-ColorText "  -EnvName <name>        虚拟环境名称 (默认: long-novel-gpt)" "White"
    Write-ColorText "  -PythonVersion <ver>   Python版本 (默认: 3.10)" "White"
    Write-ColorText "  -Force                 强制执行，不询问确认" "White"
    Write-ColorText ""
    Write-ColorText "示例:" "Yellow"
    Write-ColorText "  .\env_manager.ps1 -Command create" "White"
    Write-ColorText "  .\env_manager.ps1 -Command delete -Force" "White"
    Write-ColorText "  .\env_manager.ps1 -Command info -EnvName my-env" "White"
    Write-ColorText ""
}

# 检查conda是否安装
function Test-CondaInstalled {
    try {
        $condaVersion = conda --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ Conda 已安装: $condaVersion" "Green"
            return $true
        } else {
            throw "Conda not found"
        }
    } catch {
        Write-ColorText "✗ Conda 未安装或未添加到PATH" "Red"
        Write-ColorText "请先安装 Anaconda 或 Miniconda" "Yellow"
        Write-ColorText "下载地址: https://www.anaconda.com/products/distribution" "Yellow"
        return $false
    }
}

# 检查环境是否存在
function Test-EnvExists {
    param([string]$Name)
    try {
        $envList = conda info --envs 2>$null
        return ($envList -match [regex]::Escape($Name))
    } catch {
        return $false
    }
}

# 创建虚拟环境
function New-Environment {
    param(
        [string]$Name,
        [string]$Version
    )
    
    Write-ColorText "🔧 创建虚拟环境 $Name..." "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    if (Test-EnvExists -Name $Name) {
        Write-ColorText "⚠ 虚拟环境 $Name 已存在" "Yellow"
        if (-not $Force) {
            $choice = Read-Host "是否要删除现有环境并重新创建？ (y/N)"
            if ($choice -ne "y" -and $choice -ne "Y") {
                Write-ColorText "取消创建" "Yellow"
                return
            }
        }
        Remove-Environment -Name $Name -Force
    }
    
    Write-ColorText "正在创建虚拟环境..." "Blue"
    try {
        conda create -n $Name python=$Version -y
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ 虚拟环境创建成功" "Green"
        } else {
            throw "Failed to create environment"
        }
    } catch {
        Write-ColorText "✗ 创建虚拟环境失败" "Red"
        return
    }
    
    Write-ColorText ""
    Write-ColorText "正在激活虚拟环境..." "Blue"
    try {
        conda activate $Name
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ 虚拟环境已激活" "Green"
        } else {
            throw "Failed to activate environment"
        }
    } catch {
        Write-ColorText "✗ 激活虚拟环境失败" "Red"
        Write-ColorText "请手动激活环境: conda activate $Name" "Yellow"
        return
    }
    
    Write-ColorText ""
    Write-ColorText "正在安装项目依赖..." "Blue"
    if (Test-Path "requirements.txt") {
        try {
            pip install -r requirements.txt
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✓ 依赖安装成功" "Green"
            } else {
                throw "Failed to install dependencies"
            }
        } catch {
            Write-ColorText "✗ 安装依赖失败" "Red"
            return
        }
    } else {
        Write-ColorText "⚠ 未找到 requirements.txt 文件" "Yellow"
        Write-ColorText "请手动安装依赖: pip install -r requirements.txt" "Yellow"
    }
    
    Write-ColorText ""
    Write-ColorText "🎉 环境创建完成！" "Green"
    Write-ColorText "要激活环境，请运行: conda activate $Name" "Yellow"
    Write-ColorText "要开始开发，请运行: .\start_local.ps1" "Yellow"
    Write-ColorText ""
}

# 删除虚拟环境
function Remove-Environment {
    param(
        [string]$Name,
        [switch]$Force
    )
    
    Write-ColorText "🗑️ 删除虚拟环境 $Name..." "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    if (-not (Test-EnvExists -Name $Name)) {
        Write-ColorText "⚠ 虚拟环境 $Name 不存在" "Yellow"
        return
    }
    
    if (-not $Force) {
        Write-ColorText "警告: 这将永久删除虚拟环境 $Name 及其所有包" "Red"
        $choice = Read-Host "确定要删除吗？ (y/N)"
        if ($choice -ne "y" -and $choice -ne "Y") {
            Write-ColorText "取消删除" "Yellow"
            return
        }
    }
    
    Write-ColorText "正在删除虚拟环境 $Name..." "Blue"
    try {
        conda deactivate 2>$null
        conda env remove -n $Name -y
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ 虚拟环境已删除" "Green"
        } else {
            throw "Failed to remove environment"
        }
    } catch {
        Write-ColorText "✗ 删除虚拟环境失败" "Red"
        return
    }
    
    Write-ColorText ""
    Write-ColorText "🎉 环境删除完成！" "Green"
    Write-ColorText ""
}

# 激活虚拟环境
function Start-Environment {
    param([string]$Name)
    
    Write-ColorText "🔄 激活虚拟环境 $Name..." "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    if (-not (Test-EnvExists -Name $Name)) {
        Write-ColorText "⚠ 虚拟环境 $Name 不存在" "Yellow"
        $choice = Read-Host "是否要创建新环境？ (y/N)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            New-Environment -Name $Name -Version $PythonVersion
            return
        } else {
            Write-ColorText "取消操作" "Yellow"
            return
        }
    }
    
    Write-ColorText "要激活环境，请在新的PowerShell窗口中运行:" "Green"
    Write-ColorText "conda activate $Name" "Cyan"
    Write-ColorText ""
    Write-ColorText "或者直接运行启动脚本:" "Green"
    Write-ColorText ".\start_local.ps1" "Cyan"
    Write-ColorText ""
}

# 显示环境信息
function Get-EnvironmentInfo {
    param([string]$Name)
    
    Write-ColorText "📋 环境信息" "Blue"
    Write-ColorText "============" "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    $envExists = Test-EnvExists -Name $Name
    
    Write-ColorText "环境名称: $Name" "Yellow"
    Write-ColorText "Python版本: $PythonVersion" "Yellow"
    Write-ColorText "环境状态: " "Yellow" -NoNewline
    if ($envExists) {
        Write-ColorText "✓ 已创建" "Green"
    } else {
        Write-ColorText "✗ 未创建" "Red"
    }
    
    Write-ColorText ""
    Write-ColorText "环境路径:" "Yellow"
    conda info --envs | Select-String $Name
    
    if ($envExists) {
        Write-ColorText ""
        Write-ColorText "已安装的包 (前20个):" "Yellow"
        try {
            conda activate $Name 2>$null
            conda list | Select-Object -First 20
        } catch {
            Write-ColorText "无法列出包信息" "Red"
        }
    }
    Write-ColorText ""
}

# 列出所有环境
function Get-AllEnvironments {
    Write-ColorText "📋 所有Conda环境" "Blue"
    Write-ColorText "=================" "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    conda info --envs
    Write-ColorText ""
}

# 清理并重新安装依赖
function Reset-Environment {
    param([string]$Name)
    
    Write-ColorText "🧹 清理环境 $Name..." "Blue"
    Write-ColorText ""
    
    if (-not (Test-CondaInstalled)) {
        return
    }
    
    if (-not (Test-EnvExists -Name $Name)) {
        Write-ColorText "⚠ 虚拟环境 $Name 不存在" "Yellow"
        $choice = Read-Host "是否要创建新环境？ (y/N)"
        if ($choice -eq "y" -or $choice -eq "Y") {
            New-Environment -Name $Name -Version $PythonVersion
        }
        return
    }
    
    if (-not $Force) {
        Write-ColorText "这将清理所有已安装的包并重新安装依赖" "Yellow"
        $choice = Read-Host "确定要继续吗？ (y/N)"
        if ($choice -ne "y" -and $choice -ne "Y") {
            Write-ColorText "取消操作" "Yellow"
            return
        }
    }
    
    Write-ColorText "正在激活环境..." "Blue"
    try {
        conda activate $Name
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to activate environment"
        }
    } catch {
        Write-ColorText "✗ 激活环境失败" "Red"
        return
    }
    
    Write-ColorText "正在清理pip缓存..." "Blue"
    pip cache purge 2>$null
    
    Write-ColorText "正在卸载所有pip包..." "Blue"
    try {
        pip freeze | Out-File -FilePath "temp_requirements.txt" -Encoding utf8
        if (Test-Path "temp_requirements.txt") {
            pip uninstall -r temp_requirements.txt -y 2>$null
            Remove-Item "temp_requirements.txt" -ErrorAction SilentlyContinue
        }
    } catch {
        Write-ColorText "清理包时出现错误，继续..." "Yellow"
    }
    
    if (Test-Path "requirements.txt") {
        Write-ColorText "正在重新安装项目依赖..." "Blue"
        try {
            pip install -r requirements.txt
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✓ 依赖重新安装成功" "Green"
            } else {
                throw "Failed to install dependencies"
            }
        } catch {
            Write-ColorText "✗ 安装依赖失败" "Red"
            return
        }
    } else {
        Write-ColorText "⚠ 未找到 requirements.txt 文件" "Yellow"
    }
    
    Write-ColorText ""
    Write-ColorText "🎉 环境清理完成！" "Green"
    Write-ColorText ""
}

# 主程序
switch ($Command.ToLower()) {
    "create" {
        New-Environment -Name $EnvName -Version $PythonVersion
    }
    "delete" {
        Remove-Environment -Name $EnvName -Force:$Force
    }
    "activate" {
        Start-Environment -Name $EnvName
    }
    "info" {
        Get-EnvironmentInfo -Name $EnvName
    }
    "list" {
        Get-AllEnvironments
    }
    "clean" {
        Reset-Environment -Name $EnvName
    }
    "help" {
        Show-Help
    }
    default {
        Write-ColorText "✗ 未知命令: $Command" "Red"
        Write-ColorText ""
        Show-Help
    }
}