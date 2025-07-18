# API配置管理文档

## 概述

本文档详细介绍Long-Novel-GPT支持的所有AI提供商的配置方法、参数说明和最佳实践。

## 支持的API提供商

### 1. DeepSeek API

**特点：**
- 高性价比，中文优化
- 支持长上下文
- 响应速度快

**配置参数：**
```json
{
  "name": "deepseek",
  "api_key": "sk-your-deepseek-api-key",
  "model_name": "deepseek-chat",
  "base_url": "https://api.deepseek.com/v1",
  "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册并登录账户
3. 在控制台中创建API密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export DEEPSEEK_API_KEY="sk-your-key-here"
export DEEPSEEK_MODEL="deepseek-chat"

# 代码配置
config = {
    "api_key": "sk-your-key-here",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com/v1",
    "max_tokens": 4096
}
```

### 2. OpenAI API

**特点：**
- 最先进的GPT模型
- 支持多种模式
- 生态系统完善

**配置参数：**
```json
{
  "name": "openai",
  "api_key": "sk-your-openai-api-key",
  "model_name": "gpt-4",
  "base_url": "https://api.openai.com/v1",
  "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [OpenAI平台](https://platform.openai.com/)
2. 注册并验证账户
3. 在API Keys页面创建新密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_MODEL="gpt-4"

# 代码配置
config = {
    "api_key": "sk-your-key-here",
    "model": "gpt-4",
    "base_url": "https://api.openai.com/v1",
    "max_tokens": 4096
}
```

### 3. OpenRouter API

**特点：**
- 聚合多个模型提供商
- 统一API接口
- 价格透明

**配置参数：**
```json
{
  "name": "openrouter",
  "api_key": "sk-your-openrouter-api-key",
  "model_name": "openai/gpt-4",
  "base_url": "https://openrouter.ai/api/v1",
  "models": [
    "openai/gpt-4",
    "anthropic/claude-3-opus",
    "google/gemini-pro",
    "deepseek/deepseek-chat"
  ],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册并登录账户
3. 在Keys页面创建API密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export OPENROUTER_API_KEY="sk-your-key-here"
export OPENROUTER_MODEL="openai/gpt-4"

# 代码配置
config = {
    "api_key": "sk-your-key-here",
    "model": "openai/gpt-4",
    "base_url": "https://openrouter.ai/api/v1",
    "max_tokens": 4096,
    "headers": {
        "HTTP-Referer": "https://github.com/Long-Novel-GPT",
        "X-Title": "Long-Novel-GPT"
    }
}
```

### 4. 智谱AI API

**特点：**
- 国产大模型
- 中文理解能力强
- 多模态支持

**配置参数：**
```json
{
  "name": "zhipuai",
  "api_key": "your-zhipuai-api-key",
  "model_name": "glm-4-air",
  "base_url": null,
  "models": ["glm-4-air", "glm-4-flashx", "glm-4-plus", "glm-4v-plus"],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并实名认证
3. 在API管理页面创建密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export ZHIPUAI_API_KEY="your-key-here"
export ZHIPUAI_MODEL="glm-4-air"

# 代码配置
config = {
    "api_key": "your-key-here",
    "model": "glm-4-air",
    "max_tokens": 4096
}
```

### 5. 阿里云API

**特点：**
- 通义千问系列
- 企业级稳定性
- 长文本处理

**配置参数：**
```json
{
  "name": "aliyun",
  "api_key": "your-aliyun-api-key",
  "model_name": "qwen-max",
  "base_url": "https://dashscope.aliyuncs.com/api/v1",
  "models": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen2.5-72b-instruct"],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [阿里云控制台](https://dashscope.console.aliyun.com/)
2. 开通灵积模型服务
3. 在API-KEY管理页面创建密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export DASHSCOPE_API_KEY="sk-your-key-here"
export QWEN_MODEL="qwen-max"

# 代码配置
config = {
    "api_key": "sk-your-key-here",
    "model": "qwen-max",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "max_tokens": 4096
}
```

### 6. 豆包API

**特点：**
- 字节跳动出品
- 多模态能力
- 高质量输出

**配置参数：**
```json
{
  "name": "doubao",
  "api_key": "your-doubao-api-key",
  "model_name": "doubao-lite-32k",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "models": ["doubao-lite-32k", "doubao-lite-128k", "doubao-pro-32k", "doubao-pro-128k"],
  "system_prompt": "",
  "endpoint_id": "your-endpoint-id"
}
```

**获取API密钥：**
1. 访问 [火山引擎](https://console.volcengine.com/ark/)
2. 开通豆包大模型服务
3. 创建推理接入点
4. 复制API Key和Endpoint ID

**使用示例：**
```python
# 环境变量配置
export DOUBAO_API_KEY="your-key-here"
export DOUBAO_ENDPOINT_ID="your-endpoint-id"

# 代码配置
config = {
    "api_key": "your-key-here",
    "model": "doubao-lite-32k",
    "endpoint_id": "your-endpoint-id",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "max_tokens": 32000
}
```

### 7. Claude API

**特点：**
- Anthropic出品
- 长文本理解能力强
- 安全性高

**配置参数：**
```json
{
  "name": "claude",
  "api_key": "sk-your-claude-api-key",
  "model_name": "claude-3-5-sonnet-20241022",
  "base_url": "https://api.anthropic.com",
  "models": [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
  ],
  "system_prompt": ""
}
```

**获取API密钥：**
1. 访问 [Anthropic控制台](https://console.anthropic.com/)
2. 注册并验证账户
3. 在API Keys页面创建密钥
4. 复制密钥到配置文件

**使用示例：**
```python
# 环境变量配置
export ANTHROPIC_API_KEY="sk-your-key-here"
export CLAUDE_MODEL="claude-3-5-sonnet-20241022"

# 代码配置
config = {
    "api_key": "sk-your-key-here",
    "model": "claude-3-5-sonnet-20241022",
    "base_url": "https://api.anthropic.com",
    "max_tokens": 4096
}
```

### 8. LM Studio（本地模型）

**特点：**
- 本地部署
- 隐私保护
- 无网络依赖

**配置参数：**
```json
{
  "name": "lmstudio",
  "api_key": "lm-studio",
  "model_name": "your-local-model",
  "base_url": "http://localhost:1234/v1",
  "models": ["your-local-model"],
  "system_prompt": ""
}
```

**设置步骤：**
1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 下载所需的模型文件
3. 启动本地服务器
4. 配置API端点

**使用示例：**
```python
# 环境变量配置
export LM_STUDIO_BASE_URL="http://localhost:1234/v1"
export LM_STUDIO_MODEL="your-local-model"

# 代码配置
config = {
    "api_key": "lm-studio",
    "model": "your-local-model",
    "base_url": "http://localhost:1234/v1",
    "max_tokens": 4096
}
```

## 配置方法

### 1. 环境变量配置

**创建.env文件：**
```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

**配置示例：**
```env
# DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key
DEEPSEEK_MODEL=deepseek-chat

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4

# 智谱AI
ZHIPUAI_API_KEY=your-zhipuai-key
ZHIPUAI_MODEL=glm-4-air

# 默认提供商
DEFAULT_PROVIDER=deepseek
```

### 2. 动态配置

**创建runtime_config.json：**
```json
{
  "current_provider": "deepseek",
  "providers": {
    "deepseek": {
      "name": "deepseek",
      "api_key": "sk-your-key",
      "model_name": "deepseek-chat",
      "base_url": "https://api.deepseek.com/v1",
      "models": ["deepseek-chat", "deepseek-coder"],
      "system_prompt": "你是一个专业的小说创作助手。"
    }
  }
}
```

### 3. Web界面配置

**通过Web界面配置：**
1. 启动应用
2. 访问设置页面
3. 选择AI提供商
4. 填写API密钥
5. 测试连接
6. 保存配置

## 配置验证

### 1. 基本连接测试

```python
def test_api_connection(provider_name, config):
    """测试API连接"""
    try:
        # 根据提供商选择测试方法
        if provider_name == "deepseek":
            return test_deepseek_connection(config)
        elif provider_name == "openai":
            return test_openai_connection(config)
        elif provider_name == "zhipuai":
            return test_zhipuai_connection(config)
        # ... 其他提供商
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_deepseek_connection(config):
    """测试DeepSeek连接"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": config["model_name"],
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    response = requests.post(
        f"{config['base_url']}/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        return {"success": True, "message": "连接成功"}
    else:
        return {"success": False, "error": response.text}
```

### 2. 模型可用性检查

```python
def check_model_availability(provider_name, config):
    """检查模型可用性"""
    try:
        # 获取模型列表
        models = get_available_models(provider_name, config)
        
        # 检查配置的模型是否在可用列表中
        if config["model_name"] in models:
            return {"success": True, "models": models}
        else:
            return {
                "success": False,
                "error": f"模型 {config['model_name']} 不可用",
                "available_models": models
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 3. 权限和配额检查

```python
def check_api_quota(provider_name, config):
    """检查API配额"""
    try:
        # 发送简单请求检查配额
        response = send_test_request(provider_name, config)
        
        if response.get("success"):
            # 检查响应头中的配额信息
            quota_info = extract_quota_info(response.get("headers", {}))
            return {"success": True, "quota": quota_info}
        else:
            return {"success": False, "error": response.get("error")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## 费用配置

### 1. 费用限制设置

```env
# 费用限制配置
API_HOURLY_LIMIT_RMB=100
API_DAILY_LIMIT_RMB=500
API_USD_TO_RMB_RATE=7.0
```

### 2. 费用监控

```python
def monitor_api_costs():
    """监控API费用"""
    from llm_api.mongodb_cost import get_model_cost_stats
    import datetime
    
    # 获取最近24小时的费用统计
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=24)
    
    stats = get_model_cost_stats(start_time, end_time)
    
    total_cost_rmb = 0
    for stat in stats:
        if stat['currency_symbol'] == '$':
            cost_rmb = stat['total_cost'] * 7.0  # USD to RMB
        else:
            cost_rmb = stat['total_cost']
        total_cost_rmb += cost_rmb
    
    print(f"最近24小时费用: ￥{total_cost_rmb:.2f}")
    
    # 检查是否超过限制
    if total_cost_rmb > 500:  # 日限制
        print("⚠️  费用超过日限制！")
    
    return total_cost_rmb
```

### 3. 费用统计

```python
def get_cost_statistics(days=7):
    """获取费用统计"""
    from llm_api.mongodb_cost import get_model_cost_stats
    import datetime
    
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=days)
    
    stats = get_model_cost_stats(start_time, end_time)
    
    cost_by_provider = {}
    for stat in stats:
        provider = stat['model'].split('/')[0] if '/' in stat['model'] else 'unknown'
        
        if provider not in cost_by_provider:
            cost_by_provider[provider] = {
                'total_cost': 0,
                'total_tokens': 0,
                'call_count': 0
            }
        
        cost_by_provider[provider]['total_cost'] += stat['total_cost']
        cost_by_provider[provider]['total_tokens'] += stat['total_tokens']
        cost_by_provider[provider]['call_count'] += stat['call_count']
    
    return cost_by_provider
```

## 最佳实践

### 1. 安全配置

**保护API密钥：**
```bash
# 设置文件权限
chmod 600 .env
chmod 600 runtime_config.json

# 使用环境变量
export API_KEY_FILE="/secure/path/to/keys"
```

**密钥轮换：**
```python
def rotate_api_key(provider_name, old_key, new_key):
    """轮换API密钥"""
    # 1. 测试新密钥
    test_result = test_api_connection(provider_name, {"api_key": new_key})
    
    if not test_result["success"]:
        return {"success": False, "error": "新密钥测试失败"}
    
    # 2. 更新配置
    config_manager = get_config_manager()
    config_manager.update_provider_config(provider_name, {"api_key": new_key})
    
    # 3. 保存配置
    config_manager.save_config_to_file()
    
    return {"success": True, "message": "密钥轮换成功"}
```

### 2. 性能优化

**连接池配置：**
```python
import httpx

# 配置连接池
client = httpx.Client(
    timeout=30.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

**请求重试：**
```python
import time
import random

def retry_api_call(func, max_retries=3, backoff_factor=1.0):
    """API调用重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 指数退避
                delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                
    return wrapper
```

### 3. 错误处理

**统一错误处理：**
```python
class APIError(Exception):
    """API错误基类"""
    def __init__(self, message, error_code=None, provider=None):
        self.message = message
        self.error_code = error_code
        self.provider = provider
        super().__init__(self.message)

class RateLimitError(APIError):
    """限流错误"""
    pass

class AuthenticationError(APIError):
    """认证错误"""
    pass

class QuotaExceededError(APIError):
    """配额超限错误"""
    pass

def handle_api_error(response, provider_name):
    """处理API错误"""
    if response.status_code == 401:
        raise AuthenticationError("API密钥无效", provider=provider_name)
    elif response.status_code == 429:
        raise RateLimitError("请求过于频繁", provider=provider_name)
    elif response.status_code == 402:
        raise QuotaExceededError("配额已用完", provider=provider_name)
    else:
        raise APIError(f"API调用失败: {response.text}", provider=provider_name)
```

### 4. 监控和告警

**设置监控：**
```python
class APIMonitor:
    def __init__(self):
        self.metrics = {
            'success_count': 0,
            'error_count': 0,
            'total_cost': 0,
            'response_times': []
        }
    
    def record_success(self, response_time, cost=0):
        self.metrics['success_count'] += 1
        self.metrics['total_cost'] += cost
        self.metrics['response_times'].append(response_time)
    
    def record_error(self, error_type):
        self.metrics['error_count'] += 1
        
        # 发送告警
        if self.metrics['error_count'] > 10:
            self.send_alert(f"API错误次数过多: {error_type}")
    
    def send_alert(self, message):
        # 实现告警逻辑（邮件、短信、Webhook等）
        print(f"🚨 告警: {message}")
```

## 故障排除

### 1. 常见错误

**认证失败：**
```
Error: 401 Unauthorized
原因: API密钥无效或过期
解决: 检查并更新API密钥
```

**限流错误：**
```
Error: 429 Too Many Requests
原因: 请求频率过高
解决: 降低请求频率或升级套餐
```

**配额超限：**
```
Error: 402 Payment Required
原因: API配额已用完
解决: 充值或等待配额重置
```

### 2. 诊断工具

**连接诊断：**
```python
def diagnose_connection(provider_name, config):
    """诊断连接问题"""
    results = {}
    
    # 1. 检查网络连接
    results['network'] = check_network_connectivity(config['base_url'])
    
    # 2. 检查DNS解析
    results['dns'] = check_dns_resolution(config['base_url'])
    
    # 3. 检查SSL证书
    results['ssl'] = check_ssl_certificate(config['base_url'])
    
    # 4. 检查API密钥
    results['auth'] = check_api_authentication(provider_name, config)
    
    # 5. 检查API状态
    results['api_status'] = check_api_status(provider_name, config)
    
    return results
```

**性能诊断：**
```python
def diagnose_performance(provider_name, config):
    """诊断性能问题"""
    import time
    
    response_times = []
    
    # 发送10个测试请求
    for i in range(10):
        start_time = time.time()
        try:
            response = send_test_request(provider_name, config)
            response_time = time.time() - start_time
            response_times.append(response_time)
        except Exception as e:
            print(f"测试请求 {i+1} 失败: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"平均响应时间: {avg_time:.2f}s")
        print(f"最大响应时间: {max_time:.2f}s")
        print(f"最小响应时间: {min_time:.2f}s")
        
        if avg_time > 5.0:
            print("⚠️  响应时间过长，可能存在性能问题")
    
    return response_times
```

## 配置模板

### 1. 生产环境配置

```json
{
  "current_provider": "deepseek",
  "providers": {
    "deepseek": {
      "name": "deepseek",
      "api_key": "${DEEPSEEK_API_KEY}",
      "model_name": "deepseek-chat",
      "base_url": "https://api.deepseek.com/v1",
      "models": ["deepseek-chat", "deepseek-coder"],
      "system_prompt": "你是一个专业的小说创作助手，请遵循以下原则：1.创作内容积极向上 2.文笔流畅优美 3.情节引人入胜"
    },
    "openai": {
      "name": "openai", 
      "api_key": "${OPENAI_API_KEY}",
      "model_name": "gpt-4",
      "base_url": "https://api.openai.com/v1",
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "system_prompt": "You are a professional novel writing assistant."
    }
  }
}
```

### 2. 开发环境配置

```json
{
  "current_provider": "lmstudio",
  "providers": {
    "lmstudio": {
      "name": "lmstudio",
      "api_key": "lm-studio",
      "model_name": "local-model",
      "base_url": "http://localhost:1234/v1",
      "models": ["local-model"],
      "system_prompt": "开发测试环境"
    }
  }
}
```

### 3. 测试环境配置

```json
{
  "current_provider": "mock",
  "providers": {
    "mock": {
      "name": "mock",
      "api_key": "test-key",
      "model_name": "mock-model",
      "base_url": "http://localhost:8080/mock",
      "models": ["mock-model"],
      "system_prompt": "测试环境"
    }
  }
}
```

## 总结

通过本文档，您应该能够：

1. **了解所有支持的API提供商**：特点、获取方法、配置参数
2. **掌握配置方法**：环境变量、动态配置、Web界面配置
3. **进行配置验证**：连接测试、模型检查、权限验证
4. **实施最佳实践**：安全配置、性能优化、错误处理
5. **解决常见问题**：故障排除、诊断工具、配置模板

正确的API配置是Long-Novel-GPT正常运行的关键，请根据实际需求选择合适的提供商和配置方案。 