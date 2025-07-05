# AI小说生成器 - 配置模板文件
# 请复制此文件为 config.py 并填入您的配置信息

# ===========================================
# API 提供商配置
# ===========================================

# 当前使用的AI提供商 (请选择一个)
# 可选值: "deepseek", "ali", "zhipu", "lmstudio", "gemini", "openrouter", "claude"
CURRENT_PROVIDER = "deepseek"

# ===========================================
# DeepSeek AI 配置
# ===========================================
DEEPSEEK_CONFIG = {
    "api_key": "your-deepseek-api-key-here",  # 请替换为您的DeepSeek API密钥
    "model_name": "deepseek-chat",            # 模型名称
    "base_url": "https://api.deepseek.com",   # API地址(通常不需要修改)
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# 阿里云通义千问配置
# ===========================================
ALI_CONFIG = {
    "api_key": "your-ali-api-key-here",       # 请替换为您的阿里云API密钥
    "model_name": "qwen-long",                # 模型名称: qwen-long, qwen-plus, qwen-turbo
    "base_url": None,                         # 使用默认地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# 智谱AI配置
# ===========================================
ZHIPU_CONFIG = {
    "api_key": "your-zhipu-api-key-here",     # 请替换为您的智谱AI API密钥
    "model_name": "glm-4",                    # 模型名称: glm-4, glm-3-turbo
    "base_url": None,                         # 使用默认地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# LM Studio 本地配置
# ===========================================
LMSTUDIO_CONFIG = {
    "api_key": "lm-studio",                   # LM Studio通常不需要真实密钥
    "model_name": "your-local-model-name",    # 请替换为您在LM Studio中加载的模型名称
    "base_url": "http://localhost:1234/v1",   # LM Studio默认地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# Google Gemini 配置
# ===========================================
GEMINI_CONFIG = {
    "api_key": "your-gemini-api-key-here",    # 请替换为您的Google AI Studio API密钥
    "model_name": "gemini-pro",               # 模型名称: gemini-pro, gemini-pro-vision, gemini-1.5-pro, gemini-1.5-flash
    "base_url": None,                         # 使用默认地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# OpenRouter 配置
# ===========================================
OPENROUTER_CONFIG = {
    "api_key": "your-openrouter-api-key-here", # 请替换为您的OpenRouter API密钥
    "model_name": "openai/gpt-4",             # 模型名称: openai/gpt-4, anthropic/claude-3-opus等
    "base_url": "https://openrouter.ai/api/v1", # OpenRouter API地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# Anthropic Claude 配置
# ===========================================
CLAUDE_CONFIG = {
    "api_key": "your-claude-api-key-here",    # 请替换为您的Anthropic API密钥
    "model_name": "claude-3-sonnet-20240229", # 模型名称: claude-3-opus-20240229, claude-3-sonnet-20240229等
    "base_url": "https://api.anthropic.com",  # Anthropic API地址
    "system_prompt": ""                       # 系统提示词(可选)
}

# ===========================================
# 高级设置
# ===========================================

# 小说生成默认设置
NOVEL_SETTINGS = {
    "default_chapters": 20,        # 默认章节数
    "enable_chapters": True,       # 默认启用章节标题
    "enable_ending": True,         # 默认启用智能结尾
    "auto_save": True,            # 默认启用自动保存
    "output_dir": "output"        # 输出目录
}

# 温度设置 (控制AI生成的随机性)
TEMPERATURE_SETTINGS = {
    "outline_writer": 0.98,       # 大纲生成器温度
    "beginning_writer": 0.80,     # 开头生成器温度
    "novel_writer": 0.81,         # 正文生成器温度
    "embellisher": 0.92,          # 润色器温度
    "memory_maker": 0.66,         # 记忆生成器温度
    "title_generator": 0.8,       # 标题生成器温度
    "ending_writer": 0.85         # 结尾生成器温度
}

# 网络设置
NETWORK_SETTINGS = {
    "timeout": 60,                # 请求超时时间(秒)
    "max_retries": 3,             # 最大重试次数
    "retry_delay": 2.0            # 重试延迟时间(秒)
}

# ===========================================
# 使用说明
# ===========================================

"""
配置说明:

1. 复制文件:
   将此文件复制为 config.py

2. 选择AI提供商:
   修改 CURRENT_PROVIDER 为您要使用的提供商

3. 填入API密钥:
   在对应的配置字典中填入您的API密钥

4. 调整设置:
   根据需要修改其他设置参数

5. 保存文件:
   保存 config.py 文件即可使用

API密钥获取方式:
- DeepSeek: https://platform.deepseek.com/
- 阿里云: https://dashscope.console.aliyun.com/
- 智谱AI: https://open.bigmodel.cn/
- LM Studio: 本地部署，无需真实密钥
- Google Gemini: https://makersuite.google.com/app/apikey
- OpenRouter: https://openrouter.ai/keys
- Anthropic Claude: https://console.anthropic.com/

注意事项:
- 请勿将 config.py 上传到公开的代码仓库
- config.py 已被添加到 .gitignore 中
- 如需分享代码，请只分享此模板文件
"""