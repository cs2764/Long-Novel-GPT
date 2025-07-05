# AI 提供商配置指南

本文档详细介绍如何配置和管理 AI 网络小说生成器中的各种 AI 提供商。

## 目录

- [配置概览](#配置概览)
- [支持的提供商](#支持的提供商)
- [配置方式](#配置方式)
- [详细配置说明](#详细配置说明)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

## 配置概览

AI 网络小说生成器支持两种配置方式：

1. **Web 界面配置**（推荐）：通过浏览器界面进行配置
2. **文件配置**：直接编辑配置文件

### 配置优先级

1. 动态配置（Web 界面修改）- 最高优先级
2. 静态配置文件 (`config.py`) - 中等优先级  
3. 默认配置模板 - 最低优先级

## 支持的提供商

目前支持以下 7 个 AI 提供商：

| 提供商 | 模型示例 | 特点 | 中文支持 |
|--------|----------|------|----------|
| **DeepSeek** | deepseek-chat | 高性价比，中文优化 | ⭐⭐⭐ |
| **OpenRouter** | openai/gpt-4 | 多模型聚合平台 | ⭐⭐ |
| **Claude** | claude-3-sonnet | 长文本处理能力强 | ⭐⭐ |
| **Gemini** | gemini-pro | Google 出品 | ⭐⭐ |
| **LM Studio** | local-model | 本地部署，隐私保护 | ⭐⭐ |
| **智谱 AI** | glm-4 | 国产大模型 | ⭐⭐⭐ |
| **阿里云** | qwen-long | 长文本模型 | ⭐⭐⭐ |

## 配置方式

### Web 界面配置（推荐）

1. **启动应用**
   ```bash
   python app.py
   ```

2. **打开配置界面**
   - 访问 `http://localhost:7860`
   - 点击页面顶部的 "⚙️ 配置设置" 区域

3. **选择提供商**
   - 在下拉菜单中选择要配置的 AI 提供商

4. **填写配置信息**
   - API Key：您的 API 密钥
   - Model Name：要使用的模型名称
   - Base URL：API 基础地址（通常使用默认值）

5. **测试连接**
   - 点击 "测试连接" 按钮验证配置
   - 确认显示 "✅ 连接成功"

6. **保存配置**
   - 点击 "保存配置" 按钮
   - 确认显示保存成功信息

### 文件配置方式

1. **编辑配置文件**
   ```bash
   # 复制配置模板（如果 config.py 不存在）
   cp config_template.py config.py
   
   # 编辑配置文件
   nano config.py  # 或使用其他编辑器
   ```

2. **设置当前提供商**
   ```python
   CURRENT_PROVIDER = "deepseek"  # 设置要使用的提供商
   ```

3. **配置提供商信息**
   ```python
   DEEPSEEK_CONFIG = {
       "api_key": "your-deepseek-api-key",
       "model_name": "deepseek-chat",
       "base_url": "https://api.deepseek.com",
       "system_prompt": ""
   }
   ```

## 详细配置说明

### DeepSeek 配置

```python
DEEPSEEK_CONFIG = {
    "api_key": "sk-xxx",                    # 必填：DeepSeek API 密钥
    "model_name": "deepseek-chat",          # 推荐：deepseek-chat 或 deepseek-coder
    "base_url": "https://api.deepseek.com", # 默认：官方 API 地址
    "system_prompt": ""                     # 可选：自定义系统提示词
}
```

**获取方式：**
1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并完成实名认证
3. 在 API Keys 页面创建新的 API 密钥

**特点：**
- 价格低廉，性价比高
- 中文理解能力强
- 支持长文本处理

### OpenRouter 配置

```python
OPENROUTER_CONFIG = {
    "api_key": "sk-or-xxx",                      # 必填：OpenRouter API 密钥
    "model_name": "openai/gpt-4",               # 推荐模型列表见下方
    "base_url": "https://openrouter.ai/api/v1", # 默认：OpenRouter API 地址
    "system_prompt": ""                          # 可选：自定义系统提示词
}
```

**推荐模型：**
- `openai/gpt-4` - OpenAI GPT-4
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet
- `meta-llama/llama-2-70b-chat` - Llama 2 70B
- `mistralai/mixtral-8x7b-instruct` - Mixtral 8x7B

**获取方式：**
1. 访问 [OpenRouter 官网](https://openrouter.ai/)
2. 注册账号并充值
3. 在 Keys 页面创建 API 密钥

### Claude 配置

```python
CLAUDE_CONFIG = {
    "api_key": "sk-ant-xxx",                        # 必填：Anthropic API 密钥
    "model_name": "claude-3-sonnet-20240229",       # 推荐：Claude 3 Sonnet
    "base_url": "https://api.anthropic.com",        # 默认：Anthropic API 地址
    "system_prompt": ""                             # 可选：自定义系统提示词
}
```

**可用模型：**
- `claude-3-haiku-20240307` - Claude 3 Haiku（快速）
- `claude-3-sonnet-20240229` - Claude 3 Sonnet（平衡）
- `claude-3-opus-20240229` - Claude 3 Opus（高质量）

**获取方式：**
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册账号并完成验证
3. 在 API Keys 页面创建密钥

### Gemini 配置

```python
GEMINI_CONFIG = {
    "api_key": "AIzaSyxxx",              # 必填：Google AI Studio API 密钥
    "model_name": "gemini-pro",          # 推荐：gemini-pro
    "base_url": None,                    # 使用默认地址
    "system_prompt": ""                  # 可选：自定义系统提示词
}
```

**获取方式：**
1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 登录 Google 账号
3. 在 API Keys 页面获取密钥

### LM Studio 配置

```python
LMSTUDIO_CONFIG = {
    "api_key": "lm-studio",                   # 固定值
    "model_name": "local-model",              # 本地模型名称
    "base_url": "http://localhost:1234/v1",   # LM Studio 本地地址
    "system_prompt": ""                       # 可选：自定义系统提示词
}
```

**设置步骤：**
1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 下载并加载本地模型
3. 启动本地服务器（默认端口 1234）
4. 确保地址 `http://localhost:1234/v1` 可访问

### 智谱 AI 配置

```python
ZHIPU_CONFIG = {
    "api_key": "xxx.xxx",                 # 必填：智谱 AI API 密钥
    "model_name": "glm-4",                # 推荐：glm-4 或 glm-3-turbo
    "base_url": None,                     # 使用默认地址
    "system_prompt": ""                   # 可选：自定义系统提示词
}
```

**获取方式：**
1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册账号并完成实名认证
3. 在 API Keys 页面创建密钥

### 阿里云配置

```python
ALI_CONFIG = {
    "api_key": "sk-xxx",                  # 必填：阿里云 API 密钥
    "model_name": "qwen-long",            # 推荐：qwen-long 或 qwen-turbo
    "base_url": None,                     # 使用默认地址
    "system_prompt": ""                   # 可选：自定义系统提示词
}
```

**获取方式：**
1. 访问 [阿里云模型服务](https://dashscope.aliyun.com/)
2. 登录阿里云账号
3. 在 API-KEY 管理页面创建密钥

## 高级配置

### 温度参数配置

可以为不同的智能体设置不同的创意程度：

```python
TEMPERATURE_SETTINGS = {
    "outline_writer": 0.98,    # 大纲作家：高创意
    "beginning_writer": 0.80,  # 开头作家：中等创意
    "novel_writer": 0.81,      # 正文作家：中等创意
    "embellisher": 0.92,       # 润色师：高创意
    "memory_maker": 0.66       # 记忆管理器：低创意
}
```

### 网络设置

```python
NETWORK_SETTINGS = {
    "timeout": 60,          # 请求超时时间（秒）
    "max_retries": 3,       # 最大重试次数
    "retry_delay": 2.0      # 重试延迟（秒）
}
```

### 小说设置

```python
NOVEL_SETTINGS = {
    "default_chapters": 20,    # 默认章节数
    "enable_chapters": True,   # 启用章节标题
    "enable_ending": True,     # 启用智能结尾
    "auto_save": True,         # 自动保存
    "output_dir": "output"     # 输出目录
}
```

## 配置验证

### 自动验证

系统会在启动时自动检查配置：

- ✅ **配置完成**：API 密钥已正确设置
- ⚠️ **需要配置**：需要设置 API 密钥
- ❌ **配置错误**：API 密钥格式不正确

### 手动测试

在 Web 界面中：

1. 选择要测试的提供商
2. 点击 "测试连接" 按钮
3. 查看测试结果：
   - ✅ **连接成功**：配置正确，可以正常使用
   - ❌ **连接失败**：检查 API 密钥和网络连接

## 常见问题

### Q: 如何切换 AI 提供商？

**A:** 有两种方式：

1. **Web 界面**：在配置区域选择不同的提供商并保存
2. **配置文件**：修改 `CURRENT_PROVIDER` 的值

### Q: 可以同时配置多个提供商吗？

**A:** 可以。您可以配置多个提供商，但同时只能使用一个作为当前提供商。

### Q: API 密钥安全吗？

**A:** 是的。API 密钥存储在本地配置文件中，不会上传到云端。请妥善保管您的密钥文件。

### Q: 如何备份配置？

**A:** 备份 `config.py` 文件即可：

```bash
cp config.py config_backup.py
```

### Q: 配置文件损坏怎么办？

**A:** 删除 `config.py` 文件，重新启动程序会自动创建新的配置文件：

```bash
rm config.py
python app.py
```

## 故障排除

### 连接失败

1. **检查 API 密钥**
   - 确认密钥格式正确
   - 确认密钥未过期
   - 确认账户有余额

2. **检查网络连接**
   - 确认可以访问互联网
   - 确认没有防火墙阻挡
   - 尝试使用 VPN（如果在中国大陆）

3. **检查模型名称**
   - 确认模型名称正确
   - 确认有权限使用该模型

### 生成质量问题

1. **调整温度参数**
   - 提高温度增加创意性
   - 降低温度增加稳定性

2. **优化提示词**
   - 修改 `system_prompt` 字段
   - 添加具体的写作要求

3. **更换模型**
   - 尝试不同的模型
   - 选择更强大的模型

### 性能问题

1. **网络优化**
   - 增加超时时间
   - 减少重试次数

2. **本地部署**
   - 使用 LM Studio 进行本地部署
   - 避免网络延迟

## 配置示例

### 多提供商配置示例

```python
# 当前使用的提供商
CURRENT_PROVIDER = "deepseek"

# DeepSeek 配置（主要）
DEEPSEEK_CONFIG = {
    "api_key": "sk-your-deepseek-key",
    "model_name": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "system_prompt": ""
}

# Claude 配置（备用）
CLAUDE_CONFIG = {
    "api_key": "sk-ant-your-claude-key",
    "model_name": "claude-3-sonnet-20240229",
    "base_url": "https://api.anthropic.com",
    "system_prompt": ""
}

# LM Studio 配置（本地）
LMSTUDIO_CONFIG = {
    "api_key": "lm-studio",
    "model_name": "chinese-llama-2-7b",
    "base_url": "http://localhost:1234/v1",
    "system_prompt": ""
}
```

---

*本文档会随着系统更新而持续完善，如有疑问请查看项目 GitHub 或提交 Issue。*