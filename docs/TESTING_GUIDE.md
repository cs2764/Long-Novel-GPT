# 测试和验证指南

本文档提供了Long-Novel-GPT项目的完整测试和验证指南，包括单元测试、集成测试、性能测试、API验证等方面。

## 📋 目录

1. [测试架构概述](#测试架构概述)
2. [测试环境配置](#测试环境配置)
3. [单元测试](#单元测试)
4. [集成测试](#集成测试)
5. [API测试](#API测试)
6. [性能测试](#性能测试)
7. [前端测试](#前端测试)
8. [自动化测试](#自动化测试)
9. [测试数据管理](#测试数据管理)
10. [测试报告](#测试报告)

## 测试架构概述

### 测试策略

```
测试金字塔
    ↑
    |  端到端测试 (E2E)
    |      ↑
    |      |  集成测试
    |      |      ↑
    |      |      |  单元测试
    |      |      |      ↑
    |      |      |      |  静态代码分析
    ↓      ↓      ↓      ↓
  少量   中等   大量   基础
```

### 测试覆盖范围

- **单元测试**: 核心业务逻辑、工具函数、API接口
- **集成测试**: 模块间交互、数据库操作、外部API调用
- **性能测试**: 响应时间、并发处理、内存使用
- **端到端测试**: 完整用户流程、界面交互

### 测试工具栈

```python
# 测试框架
pytest              # 主要测试框架
unittest            # Python标准测试库
asyncio             # 异步测试支持

# 模拟和存根
pytest-mock        # Mock对象
responses           # HTTP响应模拟
freezegun           # 时间模拟

# 覆盖率测试
pytest-cov         # 代码覆盖率
coverage            # 覆盖率报告

# 性能测试
locust              # 负载测试
memory_profiler     # 内存分析
pytest-benchmark    # 性能基准测试

# 前端测试
selenium            # 浏览器自动化
requests            # HTTP客户端测试
```

## 测试环境配置

### 1. 测试环境安装

```bash
# 安装测试依赖
pip install pytest pytest-mock pytest-cov pytest-asyncio
pip install responses freezegun locust selenium
pip install memory_profiler pytest-benchmark

# 创建测试配置文件
cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-exclude=tests/*
    --cov-exclude=venv/*
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow tests
    api: API tests
EOF
```

### 2. 测试目录结构

```
tests/
├── __init__.py
├── conftest.py              # 测试配置和fixtures
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_writer.py
│   ├── test_config.py
│   └── test_utils.py
├── integration/             # 集成测试
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_database.py
│   └── test_workflow.py
├── performance/             # 性能测试
│   ├── __init__.py
│   ├── test_load.py
│   └── test_memory.py
├── frontend/                # 前端测试
│   ├── __init__.py
│   ├── test_ui.py
│   └── test_api_integration.py
├── fixtures/                # 测试数据
│   ├── test_data.json
│   └── mock_responses.json
└── utils/                   # 测试工具
    ├── __init__.py
    ├── test_helpers.py
    └── mock_providers.py
```

### 3. 测试配置文件

```python
# tests/conftest.py
import pytest
import os
import json
from unittest.mock import Mock, patch
from core.writer import Writer
from core.dynamic_config_manager import DynamicConfigManager
from llm_api import ModelConfig

@pytest.fixture
def test_config():
    """测试配置fixture"""
    return {
        'DEEPSEEK_API_KEY': 'test-key',
        'OPENAI_API_KEY': 'test-key',
        'MONGODB_URI': 'mongodb://localhost:27017/test_db',
        'ENABLE_MONGODB': 'false',
        'DEBUG': 'true'
    }

@pytest.fixture
def mock_model_config():
    """Mock模型配置"""
    return ModelConfig(
        model='test-model',
        api_key='test-key',
        max_tokens=1000,
        base_url='http://localhost:1234/v1'
    )

@pytest.fixture
def mock_writer():
    """Mock写作器"""
    writer = Mock(spec=Writer)
    writer.generate_text.return_value = "测试生成的文本"
    return writer

@pytest.fixture
def test_data_loader():
    """测试数据加载器"""
    def load_test_data(filename):
        with open(f'tests/fixtures/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    return load_test_data

@pytest.fixture(scope="session")
def test_app():
    """测试应用fixture"""
    from backend.app import app
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(test_app):
    """测试客户端"""
    return test_app.test_client()

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """测试后清理"""
    yield
    # 清理测试数据
    import tempfile
    import shutil
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith('test_'):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass
```

## 单元测试

### 1. 核心功能测试

```python
# tests/unit/test_writer.py
import pytest
from unittest.mock import Mock, patch
from core.writer import Writer
from core.draft_writer import DraftWriter
from llm_api import ModelConfig

class TestWriter:
    def test_writer_initialization(self):
        """测试写作器初始化"""
        writer = Writer()
        assert writer is not None
        assert hasattr(writer, 'generate_text')
    
    def test_model_config_validation(self):
        """测试模型配置验证"""
        # 有效配置
        config = ModelConfig(
            model='test-model',
            api_key='test-key',
            max_tokens=1000
        )
        assert config['model'] == 'test-model'
        assert config['api_key'] == 'test-key'
        assert config['max_tokens'] == 1000
        
        # 无效配置
        with pytest.raises(ValueError):
            ModelConfig(
                model='test-model',
                # 缺少必需的api_key
                max_tokens=1000
            )
    
    @patch('llm_api.stream_chat')
    def test_text_generation(self, mock_stream_chat):
        """测试文本生成"""
        # 设置mock返回值
        mock_stream_chat.return_value = iter([
            Mock(content="测试生成的文本")
        ])
        
        writer = Writer()
        result = writer.generate_text("测试提示词")
        
        assert result is not None
        assert "测试生成的文本" in result
        mock_stream_chat.assert_called_once()
    
    def test_chunk_processing(self):
        """测试文本块处理"""
        writer = DraftWriter()
        
        # 测试数据
        chunks = [
            ("章节1", "原始内容1"),
            ("章节2", "原始内容2")
        ]
        
        processed = writer.process_chunks(chunks)
        
        assert len(processed) == 2
        assert all(chunk[0] for chunk in processed)  # 标题不为空
        assert all(chunk[1] for chunk in processed)  # 内容不为空
    
    def test_error_handling(self):
        """测试错误处理"""
        writer = Writer()
        
        # 测试空输入
        with pytest.raises(ValueError):
            writer.generate_text("")
        
        # 测试超长输入
        with pytest.raises(ValueError):
            writer.generate_text("x" * 10000)
```

### 2. 配置管理测试

```python
# tests/unit/test_config.py
import pytest
import json
import tempfile
from unittest.mock import patch, mock_open
from core.dynamic_config_manager import DynamicConfigManager

class TestDynamicConfigManager:
    def test_config_initialization(self):
        """测试配置初始化"""
        manager = DynamicConfigManager()
        assert manager is not None
        assert manager.get_current_provider() is not None
    
    def test_provider_config_update(self):
        """测试提供商配置更新"""
        manager = DynamicConfigManager()
        
        # 测试配置更新
        config = {
            'api_key': 'new-test-key',
            'base_url': 'https://api.test.com'
        }
        
        result = manager.update_provider_config('test_provider', config)
        assert result is True
        
        # 验证配置已更新
        updated_config = manager.get_provider_config('test_provider')
        assert updated_config.api_key == 'new-test-key'
        assert updated_config.base_url == 'https://api.test.com'
    
    def test_config_persistence(self):
        """测试配置持久化"""
        manager = DynamicConfigManager()
        
        # 模拟配置保存
        with patch('builtins.open', mock_open()) as mock_file:
            manager.save_config_to_file()
            mock_file.assert_called_once()
    
    def test_config_validation(self):
        """测试配置验证"""
        manager = DynamicConfigManager()
        
        # 有效配置
        valid_config = {
            'api_key': 'valid-key',
            'model_name': 'test-model'
        }
        assert manager.validate_config(valid_config) is True
        
        # 无效配置
        invalid_config = {
            'api_key': '',  # 空API密钥
            'model_name': 'test-model'
        }
        assert manager.validate_config(invalid_config) is False
```

### 3. 工具函数测试

```python
# tests/unit/test_utils.py
import pytest
from core.writer_utils import KeyPointMsg, process_text, format_output
from core.parser_utils import parse_yaml_content, extract_sections

class TestUtilFunctions:
    def test_text_processing(self):
        """测试文本处理函数"""
        # 测试基本文本处理
        input_text = "  这是一个测试文本  \n\n  "
        result = process_text(input_text)
        assert result == "这是一个测试文本"
        
        # 测试空文本
        assert process_text("") == ""
        assert process_text(None) == ""
        
        # 测试特殊字符
        special_text = "测试\t\n\r特殊字符"
        result = process_text(special_text)
        assert "\t" not in result
        assert "\n" not in result
        assert "\r" not in result
    
    def test_yaml_parsing(self):
        """测试YAML解析"""
        yaml_content = """
        title: 测试标题
        chapters:
          - name: 第一章
            content: 第一章内容
          - name: 第二章
            content: 第二章内容
        """
        
        result = parse_yaml_content(yaml_content)
        assert result['title'] == '测试标题'
        assert len(result['chapters']) == 2
        assert result['chapters'][0]['name'] == '第一章'
    
    def test_section_extraction(self):
        """测试段落提取"""
        text = """
        # 第一章
        这是第一章的内容
        
        # 第二章
        这是第二章的内容
        """
        
        sections = extract_sections(text)
        assert len(sections) == 2
        assert sections[0]['title'] == '第一章'
        assert sections[1]['title'] == '第二章'
    
    def test_format_output(self):
        """测试输出格式化"""
        data = {
            'title': '测试标题',
            'content': '测试内容',
            'metadata': {'author': '测试作者'}
        }
        
        # 测试JSON格式
        json_output = format_output(data, 'json')
        assert '"title"' in json_output
        assert '"测试标题"' in json_output
        
        # 测试YAML格式
        yaml_output = format_output(data, 'yaml')
        assert 'title: 测试标题' in yaml_output
        
        # 测试纯文本格式
        text_output = format_output(data, 'text')
        assert '测试标题' in text_output
        assert '测试内容' in text_output
```

## 集成测试

### 1. API集成测试

```python
# tests/integration/test_api.py
import pytest
import requests
import json
from unittest.mock import patch

class TestAPIIntegration:
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_write_endpoint(self, client):
        """测试写作端点"""
        request_data = {
            'writer_mode': 'draft',
            'chunk_list': [['章节1', '原始内容1']],
            'chunk_span': [0, 1],
            'prompt_content': '测试提示词',
            'x_chunk_length': 100,
            'y_chunk_length': 200,
            'main_model': 'test/model',
            'sub_model': 'test/model',
            'global_context': '测试上下文',
            'only_prompt': False,
            'settings': {
                'MAX_THREAD_NUM': 1
            }
        }
        
        with patch('backend.backend_utils.get_model_config_from_provider_model') as mock_config:
            mock_config.return_value = {
                'model': 'test-model',
                'api_key': 'test-key',
                'max_tokens': 1000
            }
            
            response = client.post('/write', 
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            assert response.mimetype == 'text/event-stream'
    
    def test_prompts_endpoint(self, client):
        """测试提示词端点"""
        response = client.get('/prompts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'outline' in data
        assert 'plot' in data
        assert 'draft' in data
    
    def test_settings_endpoint(self, client):
        """测试设置端点"""
        response = client.get('/setting')
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert 'MAIN_MODEL' in data
        assert 'SUB_MODEL' in data
```

### 2. 数据库集成测试

```python
# tests/integration/test_database.py
import pytest
from unittest.mock import patch, Mock
from llm_api.mongodb_cache import llm_api_cache
from llm_api.mongodb_cost import CostTracker

class TestDatabaseIntegration:
    @pytest.fixture
    def mock_mongodb(self):
        """Mock MongoDB连接"""
        with patch('pymongo.MongoClient') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_client.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            yield mock_client, mock_db, mock_collection
    
    def test_cache_operations(self, mock_mongodb):
        """测试缓存操作"""
        mock_client, mock_db, mock_collection = mock_mongodb
        
        # 测试缓存存储
        cache_key = "test_key"
        cache_value = {"result": "test_result"}
        
        # 模拟缓存查找（未命中）
        mock_collection.find_one.return_value = None
        
        # 模拟缓存存储
        mock_collection.insert_one.return_value = Mock(inserted_id="test_id")
        
        # 执行缓存操作
        @llm_api_cache()
        def test_function():
            return cache_value
        
        result = test_function()
        assert result == cache_value
    
    def test_cost_tracking(self, mock_mongodb):
        """测试成本追踪"""
        mock_client, mock_db, mock_collection = mock_mongodb
        
        tracker = CostTracker()
        
        # 测试成本记录
        cost_data = {
            'model': 'test-model',
            'tokens': 1000,
            'cost': 0.01,
            'timestamp': '2023-01-01T00:00:00'
        }
        
        mock_collection.insert_one.return_value = Mock(inserted_id="cost_id")
        
        result = tracker.record_cost(cost_data)
        assert result is not None
        mock_collection.insert_one.assert_called_once()
    
    def test_database_connection_error(self):
        """测试数据库连接错误"""
        with patch('pymongo.MongoClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            # 测试连接失败时的处理
            @llm_api_cache()
            def test_function():
                return {"result": "test"}
            
            # 应该能够正常运行（不使用缓存）
            result = test_function()
            assert result == {"result": "test"}
```

### 3. 工作流集成测试

```python
# tests/integration/test_workflow.py
import pytest
from unittest.mock import patch, Mock
from core.draft_writer import DraftWriter
from core.plot_writer import PlotWriter
from core.outline_writer import OutlineWriter

class TestWorkflowIntegration:
    def test_complete_writing_workflow(self):
        """测试完整写作流程"""
        # 准备测试数据
        chunks = [
            ("章节1", "原始内容1"),
            ("章节2", "原始内容2")
        ]
        
        # Mock模型配置
        mock_config = {
            'model': 'test-model',
            'api_key': 'test-key',
            'max_tokens': 1000
        }
        
        with patch('llm_api.stream_chat') as mock_stream:
            # 设置mock返回值
            mock_stream.return_value = iter([
                Mock(content="改进后的内容1"),
                Mock(content="改进后的内容2")
            ])
            
            # 创建写作器
            writer = DraftWriter(
                xy_pairs=chunks,
                model=mock_config,
                sub_model=mock_config
            )
            
            # 执行写作
            result = writer.write("改进这些内容")
            
            # 验证结果
            assert result is not None
            mock_stream.assert_called()
    
    def test_multi_stage_workflow(self):
        """测试多阶段工作流"""
        # 阶段1：大纲生成
        outline_writer = OutlineWriter()
        
        with patch('llm_api.stream_chat') as mock_stream:
            mock_stream.return_value = iter([
                Mock(content="生成的大纲")
            ])
            
            outline = outline_writer.generate_outline("科幻小说")
            assert outline is not None
        
        # 阶段2：剧情生成
        plot_writer = PlotWriter()
        
        with patch('llm_api.stream_chat') as mock_stream:
            mock_stream.return_value = iter([
                Mock(content="生成的剧情")
            ])
            
            plot = plot_writer.generate_plot(outline)
            assert plot is not None
        
        # 阶段3：正文生成
        draft_writer = DraftWriter()
        
        with patch('llm_api.stream_chat') as mock_stream:
            mock_stream.return_value = iter([
                Mock(content="生成的正文")
            ])
            
            draft = draft_writer.generate_draft(plot)
            assert draft is not None
```

## API测试

### 1. 外部API测试

```python
# tests/api/test_external_apis.py
import pytest
import requests
import responses
from llm_api.openai_api import stream_chat_with_gpt
from llm_api.doubao_api import stream_chat_with_doubao
from llm_api.zhipuai_api import stream_chat_with_zhipuai

class TestExternalAPIs:
    @responses.activate
    def test_openai_api_success(self):
        """测试OpenAI API成功调用"""
        # 模拟API响应
        responses.add(
            responses.POST,
            'https://api.openai.com/v1/chat/completions',
            json={
                "choices": [
                    {
                        "delta": {"content": "测试响应"},
                        "finish_reason": None
                    }
                ]
            },
            status=200
        )
        
        messages = [{"role": "user", "content": "测试消息"}]
        
        # 测试API调用
        result = list(stream_chat_with_gpt(
            messages=messages,
            api_key="test-key",
            model="gpt-3.5-turbo"
        ))
        
        assert len(result) > 0
        assert result[-1][-1]['content'] == "测试响应"
    
    @responses.activate
    def test_openai_api_error(self):
        """测试OpenAI API错误处理"""
        # 模拟API错误响应
        responses.add(
            responses.POST,
            'https://api.openai.com/v1/chat/completions',
            json={"error": {"message": "Invalid API key"}},
            status=401
        )
        
        messages = [{"role": "user", "content": "测试消息"}]
        
        # 测试错误处理
        with pytest.raises(Exception) as exc_info:
            list(stream_chat_with_gpt(
                messages=messages,
                api_key="invalid-key",
                model="gpt-3.5-turbo"
            ))
        
        assert "Invalid API key" in str(exc_info.value)
    
    def test_api_timeout(self):
        """测试API超时"""
        messages = [{"role": "user", "content": "测试消息"}]
        
        with pytest.raises(Exception) as exc_info:
            list(stream_chat_with_gpt(
                messages=messages,
                api_key="test-key",
                model="gpt-3.5-turbo",
                timeout=0.001  # 很短的超时时间
            ))
        
        assert "timeout" in str(exc_info.value).lower()
    
    @responses.activate
    def test_lmstudio_api(self):
        """测试LM Studio本地API"""
        # 模拟本地API响应
        responses.add(
            responses.POST,
            'http://localhost:1234/v1/chat/completions',
            json={
                "choices": [
                    {
                        "delta": {"content": "本地模型响应"},
                        "finish_reason": None
                    }
                ]
            },
            status=200
        )
        
        messages = [{"role": "user", "content": "测试消息"}]
        
        result = list(stream_chat_with_gpt(
            messages=messages,
            api_key="lm-studio",
            base_url="http://localhost:1234/v1",
            model="local-model"
        ))
        
        assert len(result) > 0
        assert result[-1][-1]['content'] == "本地模型响应"
```

### 2. API性能测试

```python
# tests/api/test_api_performance.py
import pytest
import time
import concurrent.futures
from llm_api.openai_api import stream_chat_with_gpt

class TestAPIPerformance:
    def test_api_response_time(self):
        """测试API响应时间"""
        messages = [{"role": "user", "content": "短消息测试"}]
        
        start_time = time.time()
        
        with pytest.raises(Exception):  # 没有真实API密钥会失败
            list(stream_chat_with_gpt(
                messages=messages,
                api_key="test-key",
                model="gpt-3.5-turbo"
            ))
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 即使失败，也应该在合理时间内返回
        assert response_time < 30  # 30秒内应该返回
    
    def test_concurrent_api_calls(self):
        """测试并发API调用"""
        messages = [{"role": "user", "content": "并发测试"}]
        
        def make_api_call():
            try:
                return list(stream_chat_with_gpt(
                    messages=messages,
                    api_key="test-key",
                    model="gpt-3.5-turbo"
                ))
            except Exception:
                return None
        
        # 测试5个并发调用
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_api_call) for _ in range(5)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # 验证并发性能
        total_time = end_time - start_time
        assert total_time < 60  # 5个并发调用应该在60秒内完成
        assert len(results) == 5
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行多次API调用
        messages = [{"role": "user", "content": "内存测试"}]
        for _ in range(10):
            try:
                list(stream_chat_with_gpt(
                    messages=messages,
                    api_key="test-key",
                    model="gpt-3.5-turbo"
                ))
            except Exception:
                pass
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该控制在合理范围内（50MB）
        assert memory_increase < 50 * 1024 * 1024
```

## 性能测试

### 1. 负载测试

```python
# tests/performance/test_load.py
import pytest
import time
import threading
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """测试开始时的初始化"""
        self.client.headers.update({
            'Content-Type': 'application/json'
        })
    
    @task(3)
    def test_health_endpoint(self):
        """测试健康检查端点负载"""
        self.client.get("/health")
    
    @task(1)
    def test_prompts_endpoint(self):
        """测试提示词端点负载"""
        self.client.get("/prompts")
    
    @task(1)
    def test_settings_endpoint(self):
        """测试设置端点负载"""
        self.client.get("/setting")

class TestPerformance:
    def test_response_time_under_load(self):
        """测试负载下的响应时间"""
        import requests
        import threading
        
        results = []
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get('http://localhost:7869/health')
                end_time = time.time()
                results.append({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                results.append({'error': str(e)})
        
        # 创建10个并发线程
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        successful_requests = [r for r in results if 'status_code' in r]
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            assert avg_response_time < 5.0  # 平均响应时间应小于5秒
            assert all(r['status_code'] == 200 for r in successful_requests)
    
    def test_memory_usage_under_load(self):
        """测试负载下的内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 模拟高负载
        for i in range(100):
            # 创建大量对象
            data = [f"测试数据{j}" for j in range(1000)]
            
            # 检查内存增长
            if i % 10 == 0:
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory
                
                # 内存增长不应超过100MB
                assert memory_increase < 100 * 1024 * 1024
```

### 2. 基准测试

```python
# tests/performance/test_benchmarks.py
import pytest
import time
from core.writer_utils import process_text
from core.parser_utils import parse_yaml_content

class TestBenchmarks:
    def test_text_processing_benchmark(self, benchmark):
        """文本处理性能基准测试"""
        test_text = "这是一个测试文本 " * 1000
        
        result = benchmark(process_text, test_text)
        
        assert result is not None
        assert len(result) > 0
    
    def test_yaml_parsing_benchmark(self, benchmark):
        """YAML解析性能基准测试"""
        yaml_content = """
        title: 测试标题
        chapters:
        """ + "\n".join([f"  - name: 第{i}章\n    content: 第{i}章内容" for i in range(100)])
        
        result = benchmark(parse_yaml_content, yaml_content)
        
        assert result is not None
        assert 'title' in result
        assert len(result['chapters']) == 100
    
    def test_large_data_processing(self):
        """大数据处理性能测试"""
        # 创建大量测试数据
        large_data = ["测试数据行" + str(i) for i in range(10000)]
        
        start_time = time.time()
        
        # 处理大量数据
        processed_data = [process_text(line) for line in large_data]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证处理结果
        assert len(processed_data) == 10000
        assert processing_time < 10.0  # 处理10000条数据应在10秒内完成
        
        # 验证处理速度
        items_per_second = len(large_data) / processing_time
        assert items_per_second > 1000  # 每秒处理超过1000条
```

## 前端测试

### 1. UI自动化测试

```python
# tests/frontend/test_ui.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUI:
    @pytest.fixture
    def driver(self):
        """浏览器驱动fixture"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_page_load(self, driver):
        """测试页面加载"""
        driver.get('http://localhost:8099')
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 验证标题
        assert "Long-Novel-GPT" in driver.title
    
    def test_settings_modal(self, driver):
        """测试设置模态框"""
        driver.get('http://localhost:8099')
        
        # 点击设置按钮
        settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "settings-btn"))
        )
        settings_btn.click()
        
        # 验证模态框出现
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal"))
        )
        assert modal.is_displayed()
    
    def test_provider_selection(self, driver):
        """测试提供商选择"""
        driver.get('http://localhost:8099')
        
        # 打开设置
        settings_btn = driver.find_element(By.CLASS_NAME, "settings-btn")
        settings_btn.click()
        
        # 选择提供商
        provider_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "provider-select"))
        )
        
        # 验证选项存在
        options = provider_select.find_elements(By.TAG_NAME, "option")
        assert len(options) > 0
        
        # 验证默认选择
        selected_option = provider_select.find_element(By.CSS_SELECTOR, "option:checked")
        assert selected_option is not None
    
    def test_text_generation(self, driver):
        """测试文本生成功能"""
        driver.get('http://localhost:8099')
        
        # 输入提示词
        prompt_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prompt-input"))
        )
        prompt_input.send_keys("测试提示词")
        
        # 点击生成按钮
        generate_btn = driver.find_element(By.CLASS_NAME, "generate-btn")
        generate_btn.click()
        
        # 验证生成过程（可能需要等待）
        # 这里应该添加对生成结果的验证
        # 由于实际生成需要API调用，这里只验证UI状态变化
        
        # 验证按钮状态变化
        WebDriverWait(driver, 5).until(
            lambda d: generate_btn.text != "开始生成"
        )
```

### 2. 前端API集成测试

```python
# tests/frontend/test_api_integration.py
import pytest
import requests
import json

class TestFrontendAPIIntegration:
    def test_frontend_backend_communication(self):
        """测试前端与后端的通信"""
        # 模拟前端发送的请求
        frontend_request = {
            'writer_mode': 'draft',
            'chunk_list': [['测试章节', '测试内容']],
            'prompt_content': '测试提示词',
            'main_model': 'test/model',
            'sub_model': 'test/model',
            'settings': {
                'MAX_THREAD_NUM': 1
            }
        }
        
        # 发送请求到后端
        response = requests.post(
            'http://localhost:7869/write',
            json=frontend_request,
            headers={'Content-Type': 'application/json'}
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/event-stream; charset=utf-8'
    
    def test_settings_synchronization(self):
        """测试设置同步"""
        # 获取后端设置
        response = requests.get('http://localhost:7869/setting')
        assert response.status_code == 200
        
        settings = response.json()
        assert 'models' in settings
        assert 'MAIN_MODEL' in settings
        assert 'SUB_MODEL' in settings
        
        # 验证设置格式
        assert isinstance(settings['models'], dict)
        assert isinstance(settings['MAIN_MODEL'], str)
        assert isinstance(settings['SUB_MODEL'], str)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 发送无效请求
        invalid_request = {
            'writer_mode': 'invalid_mode',
            'chunk_list': [],
            'prompt_content': ''
        }
        
        response = requests.post(
            'http://localhost:7869/write',
            json=invalid_request,
            headers={'Content-Type': 'application/json'}
        )
        
        # 验证错误响应
        assert response.status_code in [400, 422, 500]
```

## 自动化测试

### 1. CI/CD测试配置

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=core --cov=llm_api
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ -v --benchmark-only
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
```

### 2. 测试脚本

```python
# scripts/run_tests.py
#!/usr/bin/env python3
"""测试运行脚本"""

import subprocess
import sys
import os
import argparse

def run_unit_tests():
    """运行单元测试"""
    print("Running unit tests...")
    result = subprocess.run([
        'pytest', 'tests/unit/', '-v', 
        '--cov=core', '--cov=llm_api',
        '--cov-report=html', '--cov-report=term-missing'
    ])
    return result.returncode == 0

def run_integration_tests():
    """运行集成测试"""
    print("Running integration tests...")
    result = subprocess.run([
        'pytest', 'tests/integration/', '-v'
    ])
    return result.returncode == 0

def run_performance_tests():
    """运行性能测试"""
    print("Running performance tests...")
    result = subprocess.run([
        'pytest', 'tests/performance/', '-v', '--benchmark-only'
    ])
    return result.returncode == 0

def run_all_tests():
    """运行所有测试"""
    print("Running all tests...")
    result = subprocess.run([
        'pytest', 'tests/', '-v',
        '--cov=core', '--cov=llm_api',
        '--cov-report=html', '--cov-report=term-missing'
    ])
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Run tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.performance:
        success = run_performance_tests()
    elif args.all:
        success = run_all_tests()
    else:
        print("请指定测试类型: --unit, --integration, --performance, 或 --all")
        sys.exit(1)
    
    if success:
        print("✅ 所有测试通过")
        sys.exit(0)
    else:
        print("❌ 测试失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## 测试数据管理

### 1. 测试数据生成

```python
# tests/utils/test_data_generator.py
import json
import random
from datetime import datetime, timedelta

class TestDataGenerator:
    def __init__(self):
        self.fake_names = ["张三", "李四", "王五", "赵六", "钱七"]
        self.fake_titles = ["测试章节", "示例内容", "样本文本", "模拟数据", "虚拟场景"]
    
    def generate_chunk_list(self, count=5):
        """生成测试文本块列表"""
        return [
            [f"第{i+1}章", f"这是第{i+1}章的内容，包含一些测试文本。"]
            for i in range(count)
        ]
    
    def generate_novel_data(self):
        """生成测试小说数据"""
        return {
            "title": random.choice(self.fake_titles),
            "author": random.choice(self.fake_names),
            "chapters": self.generate_chunk_list(10),
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "word_count": random.randint(50000, 200000),
                "genre": random.choice(["科幻", "奇幻", "言情", "悬疑"])
            }
        }
    
    def generate_api_response(self, content_type="text"):
        """生成API响应数据"""
        if content_type == "text":
            return {
                "choices": [
                    {
                        "delta": {"content": "这是一个测试响应内容"},
                        "finish_reason": None
                    }
                ],
                "model": "test-model",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                }
            }
        elif content_type == "json":
            return {
                "choices": [
                    {
                        "delta": {"content": json.dumps({"result": "测试结果"})},
                        "finish_reason": None
                    }
                ]
            }
    
    def generate_config_data(self):
        """生成配置测试数据"""
        return {
            "providers": {
                "test_provider": {
                    "api_key": "test-key-123",
                    "base_url": "https://api.test.com/v1",
                    "model_name": "test-model",
                    "max_tokens": 1000
                }
            },
            "settings": {
                "max_thread_num": 5,
                "enable_cache": True,
                "debug_mode": False
            }
        }
    
    def save_test_data(self, data, filename):
        """保存测试数据到文件"""
        filepath = f"tests/fixtures/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

### 2. 测试数据清理

```python
# tests/utils/test_cleanup.py
import os
import tempfile
import shutil
from pathlib import Path

class TestCleanup:
    def __init__(self):
        self.temp_dirs = []
        self.temp_files = []
    
    def create_temp_dir(self, prefix="test_"):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_file(self, suffix=".txt", content=""):
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=suffix, 
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(content)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def cleanup(self):
        """清理所有临时文件和目录"""
        # 清理临时文件
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except FileNotFoundError:
                pass
        
        # 清理临时目录
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except FileNotFoundError:
                pass
        
        # 清理测试生成的缓存文件
        cache_patterns = [
            "test_*.json",
            "test_*.yaml",
            "test_*.log",
            "__pycache__",
            "*.pyc"
        ]
        
        for pattern in cache_patterns:
            for file in Path(".").glob(f"**/{pattern}"):
                try:
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        shutil.rmtree(file)
                except (FileNotFoundError, PermissionError):
                    pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

## 测试报告

### 1. 测试报告生成

```python
# scripts/generate_test_report.py
import json
import subprocess
import datetime
from pathlib import Path

def generate_coverage_report():
    """生成覆盖率报告"""
    result = subprocess.run([
        'pytest', '--cov=core', '--cov=llm_api', 
        '--cov-report=json', '--cov-report=html',
        'tests/'
    ], capture_output=True, text=True)
    
    # 读取覆盖率数据
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        return {
            'total_coverage': coverage_data['totals']['percent_covered'],
            'files_covered': len(coverage_data['files']),
            'lines_covered': coverage_data['totals']['covered_lines'],
            'lines_missing': coverage_data['totals']['missing_lines']
        }
    except FileNotFoundError:
        return None

def generate_test_summary():
    """生成测试总结报告"""
    result = subprocess.run([
        'pytest', '--json-report', '--json-report-file=test_report.json',
        'tests/'
    ], capture_output=True, text=True)
    
    try:
        with open('test_report.json', 'r') as f:
            test_data = json.load(f)
        
        return {
            'total_tests': test_data['summary']['total'],
            'passed': test_data['summary']['passed'],
            'failed': test_data['summary']['failed'],
            'errors': test_data['summary']['error'],
            'skipped': test_data['summary']['skipped'],
            'duration': test_data['duration']
        }
    except FileNotFoundError:
        return None

def generate_html_report():
    """生成HTML测试报告"""
    coverage_data = generate_coverage_report()
    test_summary = generate_test_summary()
    
    if not coverage_data or not test_summary:
        print("无法生成报告：缺少测试数据")
        return
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Long-Novel-GPT 测试报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; }}
            .passed {{ color: green; }}
            .failed {{ color: red; }}
            .coverage {{ color: blue; }}
        </style>
    </head>
    <body>
        <h1>Long-Novel-GPT 测试报告</h1>
        <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>测试总结</h2>
            <div class="metric">
                <h3>总测试数</h3>
                <p>{test_summary['total_tests']}</p>
            </div>
            <div class="metric passed">
                <h3>通过</h3>
                <p>{test_summary['passed']}</p>
            </div>
            <div class="metric failed">
                <h3>失败</h3>
                <p>{test_summary['failed']}</p>
            </div>
            <div class="metric">
                <h3>跳过</h3>
                <p>{test_summary['skipped']}</p>
            </div>
            <div class="metric">
                <h3>用时</h3>
                <p>{test_summary['duration']:.2f}秒</p>
            </div>
        </div>
        
        <div class="summary">
            <h2>代码覆盖率</h2>
            <div class="metric coverage">
                <h3>总覆盖率</h3>
                <p>{coverage_data['total_coverage']:.1f}%</p>
            </div>
            <div class="metric">
                <h3>覆盖文件数</h3>
                <p>{coverage_data['files_covered']}</p>
            </div>
            <div class="metric">
                <h3>覆盖行数</h3>
                <p>{coverage_data['lines_covered']}</p>
            </div>
            <div class="metric">
                <h3>未覆盖行数</h3>
                <p>{coverage_data['lines_missing']}</p>
            </div>
        </div>
        
        <div class="summary">
            <h2>详细报告</h2>
            <p><a href="htmlcov/index.html">查看详细覆盖率报告</a></p>
        </div>
    </body>
    </html>
    """
    
    with open('test_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("测试报告已生成: test_report.html")

if __name__ == '__main__':
    generate_html_report()
```

### 2. 持续集成报告

```yaml
# .github/workflows/test-report.yml
name: Test Report

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 每天生成报告

jobs:
  test-report:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests with coverage
      run: |
        pytest --cov=core --cov=llm_api --cov-report=xml --cov-report=html
    
    - name: Generate test report
      run: |
        python scripts/generate_test_report.py
    
    - name: Upload test report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: |
          test_report.html
          htmlcov/
          coverage.xml
    
    - name: Comment PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const coverage = fs.readFileSync('coverage.xml', 'utf8');
          const match = coverage.match(/line-rate="([^"]+)"/);
          const rate = match ? (parseFloat(match[1]) * 100).toFixed(1) : 'N/A';
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## 测试报告 📊\n\n代码覆盖率: ${rate}%\n\n[查看详细报告](https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`
          });
```

## 最佳实践

### 1. 测试编写原则

- **单一职责**：每个测试只验证一个功能点
- **独立性**：测试之间不应相互依赖
- **可重复**：测试结果应该一致
- **快速执行**：单元测试应该快速运行
- **清晰命名**：测试名称应该描述测试的目的

### 2. 测试组织

```python
# 好的测试组织结构
class TestUserAuthentication:
    def test_valid_credentials_should_return_success(self):
        """有效凭据应该返回成功"""
        pass
    
    def test_invalid_credentials_should_return_error(self):
        """无效凭据应该返回错误"""
        pass
    
    def test_expired_token_should_require_refresh(self):
        """过期令牌应该需要刷新"""
        pass
```

### 3. Mock使用原则

```python
# 合理使用Mock
def test_api_call_with_mock():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        
        result = api_function()
        
        assert result is True
        mock_post.assert_called_once()
```

## 总结

本测试指南提供了Long-Novel-GPT项目的全面测试策略，包括：

1. **完整的测试架构**：从单元测试到端到端测试
2. **实用的测试工具**：pytest、mock、selenium等
3. **自动化测试流程**：CI/CD集成和报告生成
4. **性能测试方法**：负载测试和基准测试
5. **测试数据管理**：生成、清理和维护测试数据

遵循这些测试实践可以确保系统的稳定性和可靠性。

更多详细信息请参考：
- [调试和故障排除指南](DEBUGGING_GUIDE.md)
- [快速开发指南](QUICK_DEVELOPMENT.md)
- [环境配置指南](ENVIRONMENT_SETUP.md)

---

*本文档会根据项目发展持续更新，如有疑问请查看项目GitHub或提交Issue。* 