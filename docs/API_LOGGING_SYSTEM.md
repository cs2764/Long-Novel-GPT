# API调试日志系统文档

## 概述

Long-Novel-GPT 3.0 Enhanced Edition 实现了完整的API调试和监控系统，提供详细的HTTP请求响应记录、性能监控和费用统计功能。本文档详细介绍了日志系统的架构、实现和使用方法。

## 系统架构

### 日志系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                 API调试日志系统                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │   API调用层      │  │   日志记录层     │  │  数据存储层  │ │
│  │ (各Provider API) │─►│ (Logger Module)  │─►│ (MongoDB/   │ │
│  └──────────────────┘  └──────────────────┘  │  Console)   │ │
│                                               └─────────────┘ │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │   性能监控       │  │   费用统计       │  │  错误追踪    │ │
│  │ (Response Time)  │  │ (Cost Tracking)  │  │ (Error Log) │ │
│  └──────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┤ │
│  │                 日志聚合和分析                            │ │
│  │  • 实时监控  • 统计分析  • 告警机制  • 性能报告        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心日志模块

### 1. 统一日志入口

所有API调用都通过统一的日志装饰器进行记录：

```python
from llm_api.mongodb_cache import llm_api_cache

@llm_api_cache()
def stream_chat(model_config: ModelConfig, messages: list, response_json=False) -> Generator:
    import json
    
    print(f"\n=== LLM API Stream Chat Started ===")
    print(f"Model Config: {json.dumps(dict(model_config), default=str, ensure_ascii=False)}")
    print(f"Messages Count: {len(messages)}")
    print(f"Response JSON: {response_json}")
    
    try:
        # 验证配置
        model_config.validate()
        print(f"✅ Model config validated successfully")
        
        # 处理系统提示词
        if model_config.get('system_prompt'):
            # 注入系统提示词逻辑
            pass
            
        # 调用具体的API
        for result in api_call_function(model_config, messages, response_json):
            yield result
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        raise
    finally:
        print(f"=== LLM API Stream Chat Finished ===\n")
```

### 2. 详细的API调用日志

每个API提供商都实现了详细的日志记录：

**OpenAI API日志示例：**
```python
def stream_chat_with_gpt(messages, model='gpt-3.5-turbo', response_json=False, api_key=None, base_url=None, max_tokens=4096):
    import json
    import time
    
    # 详细日志记录API调用信息
    print(f"=== OpenAI API Call Details ===")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {'***' + api_key[-8:] if api_key and len(api_key) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    print(f"First Message: {json.dumps(messages[0] if messages else {}, ensure_ascii=False)[:200]}...")
    
    # 构建HTTP请求详细信息
    api_url = f"{base_url or 'https://api.openai.com/v1'}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if base_url and "openrouter.ai" in base_url:
        headers.update({
            "HTTP-Referer": "https://github.com/Long-Novel-GPT",
            "X-Title": "Long-Novel-GPT"
        })
    
    # 显示HTTP请求详细信息
    print(f"\n🌐 === HTTP Request Details ===")
    print(f"URL: {api_url}")
    print(f"Method: POST")
    print(f"Headers:")
    for key, value in headers.items():
        if key.lower() == 'authorization':
            print(f"  {key}: Bearer ***{value.split()[-1][-8:]}")
        else:
            print(f"  {key}: {value}")
    
    try:
        print(f"🚀 Sending request to {api_url}")
        start_time = time.time()
        
        # 发送请求
        chatstream = client.chat.completions.create(...)
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s")
        
        chunk_count = 0
        first_chunk_time = None
        
        for part in chatstream:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:  # 记录前几个chunk用于调试
                print(f"📦 Chunk #{chunk_count}: {str(part)[:200]}...")
            
            yield messages
        
        total_time = time.time() - start_time
        print(f"✅ API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ API Call Failed: {type(e).__name__}: {str(e)}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        raise
    finally:
        print(f"=== OpenAI API Call Finished ===\n")
```

### 3. 智谱AI API日志

```python
def stream_chat_with_zhipuai(messages, model='glm-4-flash', response_json=False, api_key=None, max_tokens=4096):
    import json
    import time
    
    # 详细日志记录API调用信息
    print(f"=== ZhipuAI API Call Details ===")
    print(f"Model: {model}")
    print(f"API Key: {'***' + api_key[-8:] if api_key and len(api_key) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    print(f"First Message: {json.dumps(messages[0] if messages else {}, ensure_ascii=False)[:200]}...")
    
    try:
        print(f"✅ Creating ZhipuAI client...")
        client = ZhipuAI(api_key=api_key)
        print(f"✅ ZhipuAI client created successfully")
        
        print(f"\n🌐 === ZhipuAI API Request Details ===")
        print(f"Model: {model}")
        print(f"Messages Count: {len(messages)}")
        print(f"Stream: True")
        print(f"Max Tokens: {max_tokens}")
        
        # 安全显示消息内容
        safe_messages = [
            {**msg, 'content': msg['content'][:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')}
            for msg in messages
        ]
        print(f"Request Messages: {json.dumps(safe_messages, indent=2, ensure_ascii=False)}")
        print(f"=== End ZhipuAI Request Details ===\n")
        
        print(f"🚀 Sending request to ZhipuAI API")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens
        )
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s")
        
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in response:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:
                print(f"📦 Chunk #{chunk_count}: {str(chunk)[:200]}...")
            
            yield messages
        
        total_time = time.time() - start_time
        print(f"✅ ZhipuAI API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ ZhipuAI API Call Failed: {type(e).__name__}: {str(e)}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        raise
    finally:
        print(f"=== ZhipuAI API Call Finished ===\n")
```

### 4. 豆包API日志

```python
def stream_chat_with_doubao(messages, model='doubao-lite-32k', endpoint_id=None, api_key=None, max_tokens=32000):
    import json
    import time
    
    # 详细日志记录API调用信息
    print(f"=== Doubao API Call Details ===")
    print(f"Model: {model}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"API Key: {'***' + api_key[-8:] if api_key and len(api_key) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    
    try:
        print(f"✅ Creating Doubao client...")
        client = OpenAI(api_key=api_key, base_url=base_url)
        print(f"✅ Doubao client created successfully")
        
        print(f"\n🌐 === Doubao API Request Details ===")
        print(f"Base URL: {base_url}")
        print(f"Model (Endpoint ID): {endpoint_id}")
        print(f"Messages Count: {len(messages)}")
        print(f"Stream: True")
        print(f"Response Format: {'json_object' if response_json else 'text'}")
        
        print(f"🚀 Sending request to Doubao API")
        start_time = time.time()
        
        stream = client.chat.completions.create(
            model=endpoint_id,
            messages=messages,
            stream=True,
            response_format={"type": "json_object"} if response_json else None
        )
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s")
        
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in stream:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:
                print(f"📦 Chunk #{chunk_count}: {str(chunk)[:200]}...")
            
            yield messages
        
        total_time = time.time() - start_time
        print(f"✅ Doubao API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ Doubao API Call Failed: {type(e).__name__}: {str(e)}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        raise
    finally:
        print(f"=== Doubao API Call Finished ===\n")
```

## 费用统计系统

### 1. 费用记录

```python
from llm_api.mongodb_cost import record_api_cost

def record_api_cost(messages: ChatMessages):
    """记录API调用费用"""
    db = client[MONGODB_DB_NAME]
    collection = db['api_cost']

    cost_data = {
        'created_at': datetime.datetime.now(),
        'model': messages.model,
        'cost': messages.cost,
        'currency_symbol': messages.currency_symbol,
        'input_tokens': messages[:-1].count_message_tokens(),
        'output_tokens': messages[-1:].count_message_tokens(),
        'total_tokens': messages.count_message_tokens()
    }
    collection.insert_one(cost_data)
```

### 2. 费用限制检查

```python
def check_cost_limits() -> bool:
    """检查API调用费用是否超过限制"""
    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)
    day_ago = now - datetime.timedelta(days=1)
    
    # 获取统计数据
    hour_stats = get_model_cost_stats(hour_ago, now)
    day_stats = get_model_cost_stats(day_ago, now)
    
    # 计算总费用并转换为人民币
    hour_total_rmb = sum(
        stat['total_cost'] * (API_COST_LIMITS['USD_TO_RMB_RATE'] if stat['currency_symbol'] == '$' else 1)
        for stat in hour_stats
    )
    day_total_rmb = sum(
        stat['total_cost'] * (API_COST_LIMITS['USD_TO_RMB_RATE'] if stat['currency_symbol'] == '$' else 1)
        for stat in day_stats
    )
    
    # 检查是否超过限制
    if hour_total_rmb >= API_COST_LIMITS['HOURLY_LIMIT_RMB']:
        print(f"警告：最近1小时API费用（￥{hour_total_rmb:.2f}）超过限制（￥{API_COST_LIMITS['HOURLY_LIMIT_RMB']}）")
        raise Exception("最近1小时内API调用费用超过设定上限！")
    
    if day_total_rmb >= API_COST_LIMITS['DAILY_LIMIT_RMB']:
        print(f"警告：最近24小时API费用（￥{day_total_rmb:.2f}）超过限制（￥{API_COST_LIMITS['DAILY_LIMIT_RMB']}）")
        raise Exception("最近1天内API调用费用超过设定上限！")
    
    return True
```

### 3. 费用统计报告

```python
def get_model_cost_stats(start_time, end_time):
    """获取模型费用统计"""
    db = client[MONGODB_DB_NAME]
    collection = db['api_cost']
    
    pipeline = [
        {
            "$match": {
                "created_at": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "model": "$model",
                    "currency_symbol": "$currency_symbol"
                },
                "total_cost": {"$sum": "$cost"},
                "total_tokens": {"$sum": "$total_tokens"},
                "input_tokens": {"$sum": "$input_tokens"},
                "output_tokens": {"$sum": "$output_tokens"},
                "call_count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "model": "$_id.model",
                "currency_symbol": "$_id.currency_symbol",
                "total_cost": 1,
                "total_tokens": 1,
                "input_tokens": 1,
                "output_tokens": 1,
                "call_count": 1
            }
        }
    ]
    
    return list(collection.aggregate(pipeline))
```

## 缓存系统

### 1. MongoDB缓存装饰器

```python
def llm_api_cache():
    """MongoDB缓存装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查费用限制
            check_cost_limits()
            
            use_cache = kwargs.pop('use_cache', True)
            
            if not ENABLE_MONGODB_CACHE:
                use_cache = False
            
            db = client[MONGODB_DB_NAME]
            collection = db['stream_chat']
            
            # 创建缓存键
            cache_key = create_cache_key(func.__name__, args, kwargs)
            
            # 检查缓存
            if use_cache:
                cached_result = collection.find_one({"cache_key": cache_key})
                if cached_result:
                    print(f"✅ Cache hit for {func.__name__}")
                    return replay_cached_response(cached_result)
            
            # 执行函数并缓存结果
            print(f"🚀 Cache miss, executing {func.__name__}")
            
            generator = func(*args, **kwargs)
            yields_data = []
            last_time = time.time()
            
            try:
                while True:
                    current_time = time.time()
                    value = next(generator)
                    delay = current_time - last_time
                    
                    yields_data.append({
                        'index': len(value.response),
                        'delay': delay
                    })
                    
                    last_time = current_time
                    yield value
                    
            except StopIteration as e:
                return_value = e.value
                
                # 记录API调用费用
                record_api_cost(return_value)
                
                # 存储到MongoDB
                cache_data = {
                    'created_at': datetime.datetime.now(),
                    'return_value': return_value,
                    'func_name': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                    'yields': yields_data,
                    'cache_key': cache_key,
                }
                collection.insert_one(cache_data)
                
                return return_value
            
        return wrapper
    return decorator
```

### 2. 缓存重放

```python
def replay_cached_response(cached_result):
    """重放缓存的响应"""
    yields = cached_result['yields']
    return_value = cached_result['return_value']
    
    for yield_data in yields:
        # 模拟原始延迟
        delay = min(yield_data['delay'] / CACHE_REPLAY_SPEED, CACHE_REPLAY_MAX_DELAY)
        time.sleep(delay)
        
        # 重构响应消息
        response_slice = return_value.response[:yield_data['index']]
        yield ChatMessages(return_value.messages[:-1] + [{'role': 'assistant', 'content': response_slice}])
    
    return return_value
```

## 性能监控

### 1. 响应时间监控

```python
def monitor_api_performance():
    """监控API性能"""
    start_time = time.time()
    
    try:
        # API调用
        result = api_call()
        
        response_time = time.time() - start_time
        
        print(f"✅ API调用成功")
        print(f"⏱️  响应时间: {response_time:.2f}s")
        
        # 记录性能数据
        log_performance_data({
            'response_time': response_time,
            'status': 'success',
            'timestamp': datetime.datetime.now()
        })
        
        return result
        
    except Exception as e:
        response_time = time.time() - start_time
        
        print(f"❌ API调用失败")
        print(f"⏱️  响应时间: {response_time:.2f}s")
        print(f"❌ 错误: {e}")
        
        # 记录错误数据
        log_performance_data({
            'response_time': response_time,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.datetime.now()
        })
        
        raise
```

### 2. 错误率统计

```python
def get_error_rate_stats(start_time, end_time):
    """获取错误率统计"""
    db = client[MONGODB_DB_NAME]
    collection = db['api_performance']
    
    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": start_time,
                    "$lte": end_time
                }
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = list(collection.aggregate(pipeline))
    
    total_calls = sum(result['count'] for result in results)
    error_calls = sum(result['count'] for result in results if result['_id'] == 'error')
    
    error_rate = (error_calls / total_calls * 100) if total_calls > 0 else 0
    
    return {
        'total_calls': total_calls,
        'error_calls': error_calls,
        'success_calls': total_calls - error_calls,
        'error_rate': error_rate
    }
```

## 前端日志展示

### 1. 实时日志流

```python
@app.route('/api/logs/stream', methods=['GET'])
def stream_logs():
    """流式传输日志"""
    def generate():
        # 连接到日志流
        log_stream = get_log_stream()
        
        for log_entry in log_stream:
            # 格式化日志条目
            formatted_log = {
                'timestamp': log_entry['timestamp'].isoformat(),
                'level': log_entry['level'],
                'message': log_entry['message'],
                'module': log_entry.get('module', 'unknown'),
                'extra': log_entry.get('extra', {})
            }
            
            yield f"data: {json.dumps(formatted_log)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')
```

### 2. 日志查询接口

```python
@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志列表"""
    try:
        # 解析查询参数
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        level = request.args.get('level')
        module = request.args.get('module')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # 构建查询条件
        query = {}
        if start_time:
            query['timestamp'] = {'$gte': datetime.datetime.fromisoformat(start_time)}
        if end_time:
            query.setdefault('timestamp', {})['$lte'] = datetime.datetime.fromisoformat(end_time)
        if level:
            query['level'] = level
        if module:
            query['module'] = module
        
        # 查询日志
        db = client[MONGODB_DB_NAME]
        collection = db['api_logs']
        
        total = collection.count_documents(query)
        logs = list(collection.find(query)
                   .sort('timestamp', -1)
                   .skip((page - 1) * per_page)
                   .limit(per_page))
        
        # 格式化响应
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## 配置和设置

### 1. 日志级别配置

```python
# config.py
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 日志文件配置
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

# MongoDB日志配置
ENABLE_MONGODB_LOGGING = os.getenv('ENABLE_MONGODB_LOGGING', 'true').lower() == 'true'
MONGODB_LOG_COLLECTION = os.getenv('MONGODB_LOG_COLLECTION', 'api_logs')
```

### 2. 日志处理器设置

```python
import logging
import logging.handlers
from pymongo import MongoClient

def setup_logging():
    """设置日志系统"""
    # 创建根日志器
    logger = logging.getLogger('lngpt')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # MongoDB处理器
    if ENABLE_MONGODB_LOGGING:
        mongodb_handler = MongoDBHandler()
        mongodb_handler.setLevel(logging.INFO)
        logger.addHandler(mongodb_handler)
    
    return logger

class MongoDBHandler(logging.Handler):
    """MongoDB日志处理器"""
    
    def __init__(self):
        super().__init__()
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB_NAME]
        self.collection = self.db[MONGODB_LOG_COLLECTION]
    
    def emit(self, record):
        """发送日志记录到MongoDB"""
        try:
            log_entry = {
                'timestamp': datetime.datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'extra': getattr(record, 'extra', {})
            }
            
            self.collection.insert_one(log_entry)
            
        except Exception:
            # 避免日志记录失败影响主程序
            pass
```

## 使用示例

### 1. 基本日志记录

```python
import logging

# 获取日志器
logger = logging.getLogger('lngpt.api')

# 记录不同级别的日志
logger.debug("API配置详情", extra={'config': model_config})
logger.info("开始API调用", extra={'model': model_name, 'tokens': token_count})
logger.warning("API调用超时，正在重试", extra={'retry_count': 2})
logger.error("API调用失败", extra={'error': str(e), 'traceback': traceback.format_exc()})
```

### 2. 结构化日志记录

```python
def log_api_call(func):
    """API调用日志装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('lngpt.api')
        
        # 记录调用开始
        logger.info(f"API调用开始: {func.__name__}", extra={
            'function': func.__name__,
            'args': str(args)[:200],
            'kwargs': str(kwargs)[:200]
        })
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # 记录调用成功
            duration = time.time() - start_time
            logger.info(f"API调用成功: {func.__name__}", extra={
                'function': func.__name__,
                'duration': duration,
                'status': 'success'
            })
            
            return result
            
        except Exception as e:
            # 记录调用失败
            duration = time.time() - start_time
            logger.error(f"API调用失败: {func.__name__}", extra={
                'function': func.__name__,
                'duration': duration,
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            
            raise
    
    return wrapper
```

### 3. 性能监控日志

```python
class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self):
        self.logger = logging.getLogger('lngpt.performance')
    
    def log_request(self, request_id, method, url, start_time):
        """记录请求开始"""
        self.logger.info("请求开始", extra={
            'request_id': request_id,
            'method': method,
            'url': url,
            'start_time': start_time
        })
    
    def log_response(self, request_id, status_code, duration, response_size):
        """记录响应结束"""
        self.logger.info("请求完成", extra={
            'request_id': request_id,
            'status_code': status_code,
            'duration': duration,
            'response_size': response_size
        })
    
    def log_error(self, request_id, error, duration):
        """记录请求错误"""
        self.logger.error("请求错误", extra={
            'request_id': request_id,
            'error': str(error),
            'duration': duration
        })
```

## 监控和告警

### 1. 实时监控

```python
class RealTimeMonitor:
    """实时监控类"""
    
    def __init__(self):
        self.logger = logging.getLogger('lngpt.monitor')
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'total_duration': 0,
            'last_reset': time.time()
        }
    
    def record_request(self, duration, success=True):
        """记录请求指标"""
        self.metrics['request_count'] += 1
        self.metrics['total_duration'] += duration
        
        if not success:
            self.metrics['error_count'] += 1
        
        # 每分钟输出一次统计
        if time.time() - self.metrics['last_reset'] >= 60:
            self.output_metrics()
            self.reset_metrics()
    
    def output_metrics(self):
        """输出监控指标"""
        if self.metrics['request_count'] > 0:
            avg_duration = self.metrics['total_duration'] / self.metrics['request_count']
            error_rate = self.metrics['error_count'] / self.metrics['request_count'] * 100
            
            self.logger.info("性能指标", extra={
                'request_count': self.metrics['request_count'],
                'error_count': self.metrics['error_count'],
                'error_rate': error_rate,
                'avg_duration': avg_duration,
                'total_duration': self.metrics['total_duration']
            })
    
    def reset_metrics(self):
        """重置指标"""
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'total_duration': 0,
            'last_reset': time.time()
        }
```

### 2. 告警系统

```python
class AlertSystem:
    """告警系统"""
    
    def __init__(self):
        self.logger = logging.getLogger('lngpt.alert')
        self.thresholds = {
            'error_rate': 10.0,  # 错误率超过10%
            'avg_duration': 5.0,  # 平均响应时间超过5秒
            'request_count': 1000  # 每分钟请求数超过1000
        }
    
    def check_alerts(self, metrics):
        """检查告警条件"""
        alerts = []
        
        # 检查错误率
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate',
                'message': f"错误率过高: {metrics['error_rate']:.2f}%",
                'severity': 'high'
            })
        
        # 检查响应时间
        if metrics.get('avg_duration', 0) > self.thresholds['avg_duration']:
            alerts.append({
                'type': 'response_time',
                'message': f"响应时间过长: {metrics['avg_duration']:.2f}s",
                'severity': 'medium'
            })
        
        # 检查请求量
        if metrics.get('request_count', 0) > self.thresholds['request_count']:
            alerts.append({
                'type': 'request_volume',
                'message': f"请求量过高: {metrics['request_count']}",
                'severity': 'medium'
            })
        
        # 发送告警
        for alert in alerts:
            self.send_alert(alert)
    
    def send_alert(self, alert):
        """发送告警"""
        self.logger.warning(f"告警: {alert['message']}", extra={
            'alert_type': alert['type'],
            'severity': alert['severity'],
            'timestamp': datetime.datetime.now()
        })
        
        # 这里可以添加邮件、短信、webhook等通知方式
```

## 故障排除

### 1. 常见日志问题

**问题1：日志文件过大**
```python
# 解决方案：使用轮转日志
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log', maxBytes=10*1024*1024, backupCount=5
)
```

**问题2：MongoDB连接失败**
```python
# 解决方案：添加连接检查
def check_mongodb_connection():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"MongoDB连接失败: {e}")
        return False
```

**问题3：日志性能影响**
```python
# 解决方案：异步日志记录
import asyncio
import queue
import threading

class AsyncLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._log_worker)
        self.thread.daemon = True
        self.thread.start()
    
    def emit(self, record):
        self.queue.put(record)
    
    def _log_worker(self):
        while True:
            record = self.queue.get()
            if record is None:
                break
            # 处理日志记录
            self._process_record(record)
```

### 2. 调试技巧

**启用详细日志：**
```bash
export LOG_LEVEL=DEBUG
export LNGPT_DEBUG=1
python app.py
```

**查看特定模块日志：**
```python
# 只显示API相关日志
logger = logging.getLogger('lngpt.api')
logger.setLevel(logging.DEBUG)
```

**实时监控日志：**
```bash
# 实时查看日志文件
tail -f app.log

# 使用grep过滤
tail -f app.log | grep ERROR
```

## 总结

API调试日志系统为Long-Novel-GPT提供了完整的监控和调试能力：

- **详细的API调用日志**：记录完整的HTTP请求响应信息
- **性能监控**：实时跟踪响应时间和错误率
- **费用统计**：准确记录和限制API调用费用
- **缓存系统**：提高性能并减少API调用次数
- **实时监控**：支持实时日志流和告警系统
- **多种存储方式**：支持文件、MongoDB等多种日志存储
- **灵活的配置**：支持不同日志级别和输出格式

这个系统为开发者提供了强大的调试和监控工具，确保系统的稳定性和性能。 