# OpenRouter API集成指南

## 概述

OpenRouter是一个统一的API网关，提供对多个AI模型的访问。本文档详细介绍了Long-Novel-GPT项目中OpenRouter集成的实现细节。

## API端点

### 模型列表获取
- **URL**: `https://openrouter.ai/api/v1/models`
- **方法**: GET
- **认证**: 无需API Key（公开访问）
- **限制**: 每分钟最多60次请求

### 聊天完成
- **URL**: `https://openrouter.ai/api/v1/chat/completions`
- **方法**: POST
- **认证**: 需要API Key
- **格式**: OpenAI兼容格式

## 模型列表API

### 请求示例
```http
GET https://openrouter.ai/api/v1/models
Accept: application/json
User-Agent: Long-Novel-GPT/3.0.0
```

### 响应格式
```json
{
  "data": [
    {
      "id": "openai/gpt-4",
      "name": "GPT-4",
      "created": 1687882411,
      "description": "OpenAI's most capable model",
      "context_length": 8192,
      "architecture": {
        "modality": "text",
        "tokenizer": "cl100k_base",
        "instruct_type": "none"
      },
      "pricing": {
        "prompt": "0.00003",
        "completion": "0.00006",
        "image": "0.00765",
        "request": "0"
      },
      "top_provider": {
        "context_length": 8192,
        "max_completion_tokens": 4096,
        "is_moderated": true
      },
      "per_request_limits": {
        "prompt_tokens": "unlimited",
        "completion_tokens": "unlimited"
      }
    }
  ]
}
```

## 模型过滤实现

### 支持的提供商
项目中配置了以下提供商的模型过滤：

```python
SUPPORTED_PROVIDERS = {
    'openai': ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'],
    'google': ['gemini-pro', 'gemini-flash', 'gemma'],
    'anthropic': ['claude-3', 'claude-2'],
    'qwen': ['qwen-turbo', 'qwen-plus', 'qwen-max'],
    'deepseek': ['deepseek-chat', 'deepseek-coder'],
    'grok': ['grok-1'],
    'meta': ['llama-2', 'llama-3', 'codellama'],
    'mistral': ['mistral-7b', 'mistral-large'],
    'cohere': ['command-r', 'command-nightly']
}
```

### 过滤逻辑
```python
def filter_models_by_providers(models, target_providers):
    """根据提供商过滤模型列表"""
    filtered = []
    for model in models:
        model_id = model.get('id', '')
        for provider in target_providers:
            if provider in model_id.lower():
                filtered.append(model)
                break
    return filtered
```

## 动态配置管理

### 配置类结构
```python
class OpenRouterConfig:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://openrouter.ai/api/v1"
        self.models = []
        self.supported_providers = [
            'openai', 'google', 'qwen', 'deepseek', 'grok'
        ]
    
    def load_models(self):
        """从OpenRouter API加载模型列表"""
        # 实现细节见源码
        pass
```

### 模型加载流程
1. 发送GET请求到OpenRouter API
2. 解析JSON响应
3. 根据配置的提供商过滤模型
4. 更新本地模型列表
5. 返回可用模型列表

## 错误处理

### 常见错误类型
- **网络错误**: 连接超时、DNS解析失败
- **API错误**: 认证失败、请求格式错误
- **限流错误**: 超过请求频率限制
- **模型不可用**: 选择的模型暂时不可用

### 错误处理策略
```python
def handle_api_error(error):
    """处理API调用错误"""
    if isinstance(error, requests.exceptions.Timeout):
        return "请求超时，请稍后重试"
    elif isinstance(error, requests.exceptions.ConnectionError):
        return "网络连接错误，请检查网络连接"
    elif hasattr(error, 'response') and error.response.status_code == 429:
        return "请求过于频繁，请稍后重试"
    else:
        return f"API调用失败: {str(error)}"
```

## 性能优化

### 缓存机制
- 模型列表缓存时间: 1小时
- 失败重试机制: 最多3次
- 请求超时设置: 30秒

### 并发处理
- 支持多线程并发请求
- 实现连接池复用
- 自动重试失败请求

## 调试信息

### 日志格式
```
=== OpenRouter API Call Details ===
URL: https://openrouter.ai/api/v1/models
Method: GET
Headers: {...}
Response Status: 200
Response Time: 1.23s
Response Size: 45.6KB
=== End OpenRouter API Call ===
```

### 调试开关
可以通过环境变量启用详细调试信息：
```bash
export OPENROUTER_DEBUG=true
```

## 使用示例

### 基本用法
```python
from core.dynamic_config_manager import get_config_manager

config_manager = get_config_manager()
models = config_manager.load_openrouter_models()
print(f"加载了 {len(models)} 个模型")
```

### 模型测试
```python
def test_model(model_name):
    config = get_openrouter_config()
    result = config.test_model(model_name)
    return result.success
```

## 最佳实践

1. **API Key管理**: 使用环境变量存储API Key
2. **错误处理**: 实现完善的错误处理和重试机制
3. **性能监控**: 记录API调用时间和成功率
4. **缓存策略**: 合理使用缓存减少API调用
5. **日志记录**: 详细记录调试信息用于问题排查

## 故障排除

### 常见问题
1. **模型列表为空**: 检查网络连接和API可用性
2. **认证失败**: 验证API Key是否正确
3. **请求被拒绝**: 检查是否超过速率限制
4. **模型不可用**: 尝试使用其他模型

### 诊断命令
```bash
# 测试网络连接
curl -I https://openrouter.ai/api/v1/models

# 验证API Key
curl -H "Authorization: Bearer YOUR_API_KEY" https://openrouter.ai/api/v1/models
```

## 更新日志

- **v3.0.0**: 初始版本，支持基本的模型列表获取和过滤
- **v3.0.1**: 添加错误处理和重试机制
- **v3.0.2**: 优化性能和添加缓存机制