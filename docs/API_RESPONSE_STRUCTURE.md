# OpenRouter API响应数据结构详解

## 概述

本文档详细描述了OpenRouter API的响应数据结构，包括模型列表、聊天完成等接口的响应格式。

## 模型列表API响应结构

### 完整响应格式
```json
{
  "data": [
    {
      "id": "string",
      "canonical_slug": "string",
      "hugging_face_id": "string", 
      "name": "string",
      "created": "number",
      "description": "string",
      "context_length": "number",
      "architecture": {
        "modality": "string",
        "tokenizer": "string",
        "instruct_type": "string"
      },
      "pricing": {
        "prompt": "string",
        "completion": "string",
        "image": "string",
        "request": "string"
      },
      "top_provider": {
        "context_length": "number",
        "max_completion_tokens": "number",
        "is_moderated": "boolean"
      },
      "per_request_limits": {
        "prompt_tokens": "string",
        "completion_tokens": "string"
      }
    }
  ]
}
```

### 字段说明

#### 基本信息
- `id`: 模型的唯一标识符，格式为 `provider/model-name`
- `canonical_slug`: 模型的规范化标识符
- `hugging_face_id`: 对应的Hugging Face模型ID（如果有）
- `name`: 模型的显示名称
- `created`: 模型创建时间戳
- `description`: 模型描述信息

#### 技术规格
- `context_length`: 上下文长度限制
- `architecture`: 模型架构信息
  - `modality`: 模态类型（text、multimodal等）
  - `tokenizer`: 使用的分词器类型
  - `instruct_type`: 指令类型（none、vicuna、alpaca等）

#### 定价信息
- `pricing`: 定价结构
  - `prompt`: 输入token价格（美元/token）
  - `completion`: 输出token价格（美元/token）
  - `image`: 图像处理价格（美元/image）
  - `request`: 每次请求固定费用

#### 提供商信息
- `top_provider`: 主要提供商信息
  - `context_length`: 该提供商支持的上下文长度
  - `max_completion_tokens`: 最大完成token数
  - `is_moderated`: 是否启用内容审核

#### 请求限制
- `per_request_limits`: 每次请求的限制
  - `prompt_tokens`: 输入token限制
  - `completion_tokens`: 输出token限制

## 实际响应示例

### OpenAI模型示例
```json
{
  "id": "openai/gpt-4",
  "canonical_slug": "openai/gpt-4",
  "hugging_face_id": "",
  "name": "GPT-4",
  "created": 1687882411,
  "description": "OpenAI's most capable model. Able to do any language task with better quality, longer output, and consistent instruction-following.",
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
```

### Google模型示例
```json
{
  "id": "google/gemini-pro",
  "canonical_slug": "google/gemini-pro",
  "hugging_face_id": "",
  "name": "Gemini Pro",
  "created": 1701388800,
  "description": "Google's flagship multimodal model, built from the ground up for multimodal use cases.",
  "context_length": 32768,
  "architecture": {
    "modality": "multimodal",
    "tokenizer": "gemini",
    "instruct_type": "none"
  },
  "pricing": {
    "prompt": "0.000125",
    "completion": "0.000375",
    "image": "0.0025",
    "request": "0"
  },
  "top_provider": {
    "context_length": 32768,
    "max_completion_tokens": 8192,
    "is_moderated": false
  },
  "per_request_limits": {
    "prompt_tokens": "unlimited",
    "completion_tokens": "unlimited"
  }
}
```

### 中文模型示例
```json
{
  "id": "qwen/qwen-turbo",
  "canonical_slug": "qwen/qwen-turbo",
  "hugging_face_id": "Qwen/Qwen-7B-Chat",
  "name": "Qwen Turbo",
  "created": 1699747200,
  "description": "Qwen-Turbo is a large language model developed by Alibaba Cloud, optimized for Chinese and English.",
  "context_length": 8192,
  "architecture": {
    "modality": "text",
    "tokenizer": "tiktoken",
    "instruct_type": "chatml"
  },
  "pricing": {
    "prompt": "0.000001",
    "completion": "0.000002",
    "image": "0",
    "request": "0"
  },
  "top_provider": {
    "context_length": 8192,
    "max_completion_tokens": 2048,
    "is_moderated": false
  },
  "per_request_limits": {
    "prompt_tokens": "unlimited",
    "completion_tokens": "unlimited"
  }
}
```

## 聊天完成API响应结构

### 流式响应格式
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion.chunk",
  "created": 1677652288,
  "model": "openai/gpt-4",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "Hello"
      },
      "finish_reason": null
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 1,
    "total_tokens": 11
  }
}
```

### 非流式响应格式
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "openai/gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

## 错误响应结构

### 标准错误格式
```json
{
  "error": {
    "type": "authentication_error",
    "code": "invalid_api_key",
    "message": "Invalid API key provided",
    "param": null
  }
}
```

### 常见错误类型
- `authentication_error`: 认证错误
- `rate_limit_exceeded`: 速率限制超出
- `model_not_found`: 模型不存在
- `invalid_request`: 无效请求
- `server_error`: 服务器内部错误

## 数据处理最佳实践

### 模型过滤逻辑
```python
def filter_supported_models(models_data):
    """过滤支持的模型"""
    supported_providers = ['openai', 'google', 'qwen', 'deepseek', 'grok']
    filtered_models = []
    
    for model in models_data.get('data', []):
        model_id = model.get('id', '').lower()
        if any(provider in model_id for provider in supported_providers):
            filtered_models.append(model)
    
    return filtered_models
```

### 价格计算
```python
def calculate_cost(model_info, prompt_tokens, completion_tokens):
    """计算API调用成本"""
    pricing = model_info.get('pricing', {})
    prompt_cost = float(pricing.get('prompt', 0)) * prompt_tokens
    completion_cost = float(pricing.get('completion', 0)) * completion_tokens
    request_cost = float(pricing.get('request', 0))
    
    return prompt_cost + completion_cost + request_cost
```

### 上下文长度检查
```python
def check_context_limit(model_info, token_count):
    """检查是否超过上下文长度限制"""
    context_length = model_info.get('context_length', 0)
    return token_count <= context_length
```

## 数据缓存策略

### 模型列表缓存
```python
class ModelCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_models(self):
        """获取缓存的模型列表"""
        if 'models' in self.cache:
            cache_time = self.cache['models']['timestamp']
            if time.time() - cache_time < self.ttl:
                return self.cache['models']['data']
        return None
    
    def set_models(self, models):
        """设置模型列表缓存"""
        self.cache['models'] = {
            'data': models,
            'timestamp': time.time()
        }
```

## 监控和日志

### 响应时间监控
```python
def monitor_api_response(func):
    """API响应时间监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            print(f"API调用成功，响应时间: {response_time:.2f}s")
            return result
        except Exception as e:
            response_time = time.time() - start_time
            print(f"API调用失败，响应时间: {response_time:.2f}s，错误: {e}")
            raise
    return wrapper
```

### 数据质量验证
```python
def validate_model_data(model):
    """验证模型数据完整性"""
    required_fields = ['id', 'name', 'context_length', 'pricing']
    for field in required_fields:
        if field not in model:
            raise ValueError(f"Missing required field: {field}")
    
    # 验证定价信息
    pricing = model.get('pricing', {})
    if not pricing.get('prompt') or not pricing.get('completion'):
        raise ValueError("Invalid pricing information")
    
    return True
```

## 更新日志

- **v3.0.0**: 初始版本，支持基本的响应数据结构
- **v3.0.1**: 添加错误处理和数据验证
- **v3.0.2**: 优化缓存机制和监控功能