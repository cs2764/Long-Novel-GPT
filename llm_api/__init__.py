from typing import Dict, Any, Optional, Generator

from .mongodb_cache import llm_api_cache
from .baidu_api import stream_chat_with_wenxin, wenxin_model_config
from .doubao_api import stream_chat_with_doubao, doubao_model_config
from .chat_messages import ChatMessages
from .openai_api import stream_chat_with_gpt, gpt_model_config
from .zhipuai_api import stream_chat_with_zhipuai, zhipuai_model_config

class ModelConfig(dict):
    def __init__(self, model: str, **options):
        super().__init__(**options)
        self['model'] = model
        # Add system_prompt if not provided
        if 'system_prompt' not in self:
            self['system_prompt'] = ""
        # Add timeout configuration based on provider
        self._set_timeout_by_provider()
        self.validate()
    
    def _set_timeout_by_provider(self):
        """根据提供商类型设置超时时间"""
        if 'timeout' not in self:
            # 统一设置所有提供商的超时时间为300秒
            self['timeout'] = 300  # 所有提供商：5分钟
            print(f"🕐 设置API模型超时时间为5分钟")

    def validate(self):
        def check_key(provider, keys):
            for key in keys:    
                if key not in self:
                    raise ValueError(f"{provider}的API设置中未传入: {key}")
                elif not self[key].strip():
                    raise ValueError(f"{provider}的API设置中未配置: {key}")

        if self['model'] in wenxin_model_config:
            check_key('文心一言', ['ak', 'sk'])
        elif self['model'] in doubao_model_config:
            check_key('豆包', ['api_key', 'endpoint_id'])
        elif self['model'] in zhipuai_model_config:
            check_key('智谱AI', ['api_key'])
        elif self['model'] in gpt_model_config or True:
            # 其他模型名默认采用openai接口调用
            check_key('OpenAI', ['api_key'])
        
        if 'max_tokens' not in self:
            raise ValueError('ModelConfig未传入key: max_tokens')
        else:
            assert self['max_tokens'] <= 8_192, 'max_tokens最大为8192！'


    def get_api_keys(self) -> Dict[str, str]:
        return {k: v for k, v in self.items() if k not in ['model']}

@llm_api_cache()
def stream_chat(model_config: ModelConfig, messages: list, response_json=False) -> Generator:
    import json
    
    print(f"\n=== LLM API Stream Chat Started ===")
    print(f"Model Config: {json.dumps(dict(model_config), default=str, ensure_ascii=False)}")
    print(f"Messages Count: {len(messages)}")
    print(f"Response JSON: {response_json}")
    
    try:
        if isinstance(model_config, dict):
            model_config = ModelConfig(**model_config)
        
        model_config.validate()
        print(f"✅ Model config validated successfully")

        # Inject system prompt if provided
        if model_config.get('system_prompt') and model_config['system_prompt'].strip():
            # Add system prompt as the first message if not already present
            if not messages or messages[0].get('role') != 'system':
                system_message = {'role': 'system', 'content': model_config['system_prompt']}
                messages = [system_message] + list(messages)
                print(f"✅ System prompt injected: {model_config['system_prompt'][:100]}...")
            else:
                # If first message is already a system message, prepend our system prompt
                existing_system = messages[0]['content']
                combined_system = f"{model_config['system_prompt']}\n\n{existing_system}"
                messages[0]['content'] = combined_system
                print(f"✅ System prompt prepended to existing system message")

        messages = ChatMessages(messages, model=model_config['model'])
        print(f"✅ Chat messages processed, token count: {messages.count_message_tokens()}")

        assert model_config['max_tokens'] <= 8192, 'max_tokens最大为8192！'

        if messages.count_message_tokens() > model_config['max_tokens']:
            error_msg = f'请求的文本过长，超过最大tokens:{model_config["max_tokens"]}。'
            print(f"❌ Token limit exceeded: {error_msg}")
            raise Exception(error_msg)
        
        yield messages
        
        model_name = model_config['model']
        print(f"🎯 Routing to appropriate API provider for model: {model_name}")
        
        if model_name in wenxin_model_config:
            print(f"📡 Using Wenxin API for model: {model_name}")
            result = yield from stream_chat_with_wenxin(
                messages,
                model=model_config['model'],
                ak=model_config['ak'],
                sk=model_config['sk'],
                max_tokens=model_config['max_tokens'],
                response_json=response_json
            )
        elif model_name in doubao_model_config:  # doubao models
            print(f"📡 Using Doubao API for model: {model_name}")
            result = yield from stream_chat_with_doubao(
                messages,
                model=model_config['model'],
                endpoint_id=model_config['endpoint_id'],
                api_key=model_config['api_key'],
                max_tokens=model_config['max_tokens'],
                response_json=response_json
            )
        elif model_name in zhipuai_model_config:  # zhipuai models
            print(f"📡 Using ZhipuAI API for model: {model_name}")
            result = yield from stream_chat_with_zhipuai(
                messages,
                model=model_config['model'],
                api_key=model_config['api_key'],
                max_tokens=model_config['max_tokens'],
                response_json=response_json
            )
        elif model_name in gpt_model_config or True:  # openai models或其他兼容openai接口的模型
            print(f"📡 Using OpenAI-compatible API for model: {model_name}")
            print(f"Base URL: {model_config.get('base_url', 'Default OpenAI')}")
            result = yield from stream_chat_with_gpt(
                messages,
                model=model_config['model'],
                api_key=model_config['api_key'],
                base_url=model_config.get('base_url'),
                proxies=model_config.get('proxies'),
                max_tokens=model_config['max_tokens'],
                timeout=model_config.get('timeout', 300),
                response_json=response_json
            )
        else:
            error_msg = f"Unsupported model: {model_name}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        result.finished = True
        yield result
        
        print(f"✅ Stream chat completed successfully")
        return result
        
    except Exception as e:
        print(f"❌ Stream chat failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        print(f"=== LLM API Stream Chat Finished ===\n")

def test_stream_chat(model_config: ModelConfig):
    import json
    
    print(f"\n=== Testing Model Configuration ===")
    print(f"Test Model Config: {json.dumps(dict(model_config), default=str, ensure_ascii=False)}")
    
    try:
        messages = [{"role": "user", "content": "1+1=?直接输出答案即可："}]
        print(f"Test message: {messages[0]}")
        
        response_count = 0
        for response in stream_chat(model_config, messages):
            response_count += 1
            if response_count <= 3:  # Log first few responses for debugging
                if hasattr(response, 'response'):
                    print(f"📦 Test response #{response_count}: {str(response.response)[:100]}...")
                else:
                    print(f"📦 Test response #{response_count}: {str(response)[:100]}...")
            
            # Return the response content
            if hasattr(response, 'response'):
                yield response.response
            elif isinstance(response, list) and len(response) > 0:
                # Handle chat messages format
                yield response[-1].get('content', '')
        
        print(f"✅ Model test completed successfully, received {response_count} responses")
        return response
        
    except Exception as e:
        print(f"❌ Model test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        print(f"=== Model Test Finished ===\n")

# 导出必要的函数和配置
__all__ = ['ChatMessages', 'stream_chat', 'wenxin_model_config', 'doubao_model_config', 'gpt_model_config', 'zhipuai_model_config', 'ModelConfig']
