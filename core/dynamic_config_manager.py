#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态配置管理器
负责运行时动态管理AI提供商配置，支持通过Web界面实时更新设置
"""

import json
import os
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ProviderConfig:
    """AI提供商配置"""
    name: str
    api_key: str
    model_name: str
    base_url: Optional[str] = None
    models: List[str] = None
    system_prompt: str = ""
    
    def __post_init__(self):
        if self.models is None:
            self.models = []

class DynamicConfigManager:
    """动态配置管理器"""
    
    def __init__(self):
        self._config_lock = threading.RLock()
        self._current_provider = "deepseek"
        self._providers = {}
        self._load_default_configs()
        # 尝试从文件加载配置
        self.load_config_from_file()
    
    def _load_default_configs(self):
        """加载默认配置"""
        default_configs = {
            "deepseek": ProviderConfig(
                name="deepseek",
                api_key="",
                model_name="deepseek-chat",
                base_url="https://api.deepseek.com/v1",
                models=["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]
            ),
            "aliyun": ProviderConfig(
                name="aliyun",
                api_key="", 
                model_name="qwen-max",
                base_url="https://dashscope.aliyuncs.com/api/v1",
                models=["qwen-max", "qwen-plus", "qwen-turbo", "qwen2.5-72b-instruct"]
            ),
            "zhipuai": ProviderConfig(
                name="zhipuai",
                api_key="",
                model_name="glm-4-air",
                base_url=None,
                models=["glm-4-air", "glm-4-flashx", "glm-4-plus", "glm-4v-plus"]
            ),
            "lmstudio": ProviderConfig(
                name="lmstudio",
                api_key="lm-studio",
                model_name="local-model",
                base_url="http://localhost:1234/v1",
                models=["local-model"]
            ),
            "gemini": ProviderConfig(
                name="gemini",
                api_key="",
                model_name="gemini-pro",
                base_url="https://generativelanguage.googleapis.com",
                models=["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"]
            ),
            "openrouter": ProviderConfig(
                name="openrouter",
                api_key="",
                model_name="openai/gpt-4",
                base_url="https://openrouter.ai/api/v1",
                models=[
                    "openai/gpt-4", "openai/gpt-3.5-turbo",
                    "anthropic/claude-3-opus", "anthropic/claude-3-sonnet",
                    "google/gemini-pro", "meta-llama/llama-2-70b-chat"
                ]
            ),
            "claude": ProviderConfig(
                name="claude",
                api_key="",
                model_name="claude-3-5-sonnet-20241022",
                base_url="https://api.anthropic.com",
                models=[
                    "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
                    "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022"
                ]
            )
        }
        
        with self._config_lock:
            self._providers = default_configs
    
    def get_provider_list(self) -> List[str]:
        """获取所有支持的提供商列表"""
        with self._config_lock:
            return list(self._providers.keys())
    
    def get_provider_models(self, provider_name: str) -> List[str]:
        """获取指定提供商的模型列表"""
        with self._config_lock:
            if provider_name not in self._providers:
                return []
            return self._providers[provider_name].models.copy()
    
    def get_current_provider(self) -> str:
        """获取当前使用的提供商"""
        with self._config_lock:
            return self._current_provider
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """获取指定提供商的配置"""
        with self._config_lock:
            return self._providers.get(provider_name)
    
    def get_current_config(self) -> Optional[ProviderConfig]:
        """获取当前提供商的配置"""
        with self._config_lock:
            return self._providers.get(self._current_provider)
    
    def update_provider_config(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """更新提供商配置"""
        with self._config_lock:
            if provider_name not in self._providers:
                return False
            
            provider_config = self._providers[provider_name]
            
            # 更新基本配置
            if 'api_key' in config:
                provider_config.api_key = config['api_key']
            if 'model_name' in config:
                provider_config.model_name = config['model_name']
            if 'base_url' in config:
                provider_config.base_url = config['base_url']
            if 'system_prompt' in config:
                provider_config.system_prompt = config['system_prompt']
            if 'models' in config:
                provider_config.models = config['models']
                
            return True
    
    def set_current_provider(self, provider_name: str) -> bool:
        """设置当前使用的提供商"""
        with self._config_lock:
            if provider_name not in self._providers:
                return False
            self._current_provider = provider_name
            return True
    
    def save_config_to_file(self, config_path: str = "runtime_config.json"):
        """保存配置到文件"""
        try:
            config_data = {}
            
            with self._config_lock:
                config_data["current_provider"] = self._current_provider
                config_data["providers"] = {}
                
                for name, provider_config in self._providers.items():
                    config_data["providers"][name] = asdict(provider_config)
            
            # 文件操作在锁外进行
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            print(f"配置已保存到 {config_path}")
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config_from_file(self, config_path: str = "runtime_config.json"):
        """从文件加载配置"""
        if not os.path.exists(config_path):
            print(f"配置文件 {config_path} 不存在，使用默认配置")
            return False
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            with self._config_lock:
                self._current_provider = config_data.get("current_provider", "deepseek")
                
                # 加载提供商配置
                for name, provider_data in config_data.get("providers", {}).items():
                    if name in self._providers:
                        # 更新现有配置
                        config = self._providers[name]
                        config.api_key = provider_data.get("api_key", config.api_key)
                        config.model_name = provider_data.get("model_name", config.model_name)
                        config.system_prompt = provider_data.get("system_prompt", config.system_prompt)
                        if "base_url" in provider_data:
                            config.base_url = provider_data["base_url"]
                        if "models" in provider_data:
                            config.models = provider_data["models"]
            
            print(f"配置已从 {config_path} 加载")
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
    
    def validate_config(self, provider_name: str) -> bool:
        """验证配置是否有效"""
        with self._config_lock:
            if provider_name not in self._providers:
                return False
            
            config = self._providers[provider_name]
            
            # 对于非本地提供商，检查API密钥
            if provider_name != "lmstudio":
                if not config.api_key or "your-" in config.api_key.lower():
                    return False
            
            return True
    
    def test_provider_connection(self, provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试提供商连接"""
        print(f"\n=== Testing Provider Connection ===")
        print(f"Provider: {provider_name}")
        print(f"Config: {config}")
        
        try:
            # 基本验证
            if not config.get('api_key'):
                error_msg = "API密钥不能为空"
                print(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}
            
            if not config.get('model_name'):
                error_msg = "模型名称不能为空"
                print(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}
            
            # 实现真实的API连接测试
            from llm_api import test_stream_chat, ModelConfig
            
            # 构建模型配置
            model_config = ModelConfig(
                model=config['model_name'],
                api_key=config['api_key'],
                max_tokens=100  # 测试时使用小的token数
            )
            
            # 添加特定提供商的配置
            if provider_name == 'openrouter' or config.get('base_url'):
                model_config['base_url'] = config.get('base_url', 'https://openrouter.ai/api/v1')
            
            if provider_name == 'lmstudio':
                model_config['base_url'] = config.get('base_url', 'http://localhost:1234/v1')
            
            print(f"🧪 Testing with model config: {dict(model_config)}")
            
            # 执行测试
            test_result = ""
            for response in test_stream_chat(model_config):
                test_result += response
                if len(test_result) > 50:  # 限制测试响应长度
                    break
            
            print(f"✅ Connection test successful")
            print(f"Test response: {test_result[:100]}...")
            
            return {
                "success": True, 
                "message": f"连接到 {provider_name} 成功",
                "test_response": test_result[:100] + "..." if len(test_result) > 100 else test_result
            }
            
        except Exception as e:
            error_msg = f"连接测试失败: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": error_msg}
        finally:
            print(f"=== Provider Connection Test Finished ===\n")
    
    def load_provider_models(self, provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """加载提供商的模型列表"""
        try:
            if provider_name == "lmstudio":
                return self._load_lmstudio_models(config)
            elif provider_name == "openrouter":
                return self._load_openrouter_models(config)
            elif provider_name in self._providers:
                default_models = self._providers[provider_name].models
                return {"success": True, "models": default_models}
            else:
                return {"success": False, "error": "不支持的提供商"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_lmstudio_models(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """从LM Studio加载模型列表"""
        try:
            import requests
            
            base_url = config.get('base_url', 'http://localhost:1234/v1')
            api_key = config.get('api_key', 'lm-studio')
            
            # 调用LM Studio的/v1/models接口
            response = requests.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            response.raise_for_status()
            
            models_data = response.json()
            model_names = [model["id"] for model in models_data.get("data", [])]
            
            if not model_names:
                model_names = ["local-model"]  # 默认模型作为备用
            
            return {"success": True, "models": model_names}
            
        except Exception as e:
            print(f"Failed to load LM Studio models: {e}")
            return {"success": False, "error": f"无法连接到LM Studio: {str(e)}"}
    
    def _load_openrouter_models(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """从OpenRouter API加载并过滤模型列表"""
        try:
            import requests
            
            base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
            
            print(f"OpenRouter config - base_url: {base_url}")
            
            # 调用OpenRouter的/v1/models接口（不需要API key）
            url = f"{base_url}/models"
            headers = {
                "User-Agent": "Long-Novel-GPT/1.0",
                "Content-Type": "application/json"
            }
            
            print(f"Making request to: {url}")
            print(f"Headers: {headers}")
            
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            
            models_data = response.json()
            total_models = len(models_data.get("data", []))
            print(f"Total models from API: {total_models}")
            
            # 过滤指定提供商的模型
            target_providers = ["openai", "google", "qwen", "deepseek", "grok", "x-ai"]
            filtered_models = []
            
            for model in models_data.get("data", []):
                model_id = model.get("id", "")
                for provider in target_providers:
                    if model_id.startswith(f"{provider}/"):
                        filtered_models.append(model_id)
                        break
            
            print(f"Filtered models count: {len(filtered_models)}")
            print(f"First 10 filtered models: {filtered_models[:10]}")
            
            if not filtered_models:
                # 如果没有找到模型，返回默认模型
                print("No models found, using default models")
                filtered_models = [
                    "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo",
                    "google/gemini-1.5-pro", "google/gemini-1.5-flash",
                    "deepseek/deepseek-chat", "deepseek/deepseek-r1",
                    "qwen/qwen-2.5-72b-instruct", "qwen/qwen-max",
                    "x-ai/grok-beta"
                ]
            
            return {"success": True, "models": filtered_models}
            
        except Exception as e:
            print(f"Failed to load OpenRouter models: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"无法连接到OpenRouter API: {str(e)}"}
    
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置信息"""
        with self._config_lock:
            result = {
                "current_provider": self._current_provider,
                "providers": {}
            }
            
            for name, config in self._providers.items():
                # 不返回敏感信息（API密钥）
                safe_config = asdict(config)
                if safe_config.get('api_key'):
                    api_key = safe_config['api_key']
                    if len(api_key) > 8:
                        safe_config['api_key'] = api_key[:4] + "***" + api_key[-4:]
                    else:
                        safe_config['api_key'] = "***"
                
                result["providers"][name] = safe_config
            
            return result

# 全局配置管理器实例
_config_manager = None
_config_lock = threading.Lock()

def get_config_manager() -> DynamicConfigManager:
    """获取全局配置管理器实例（单例模式）"""
    global _config_manager
    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:
                _config_manager = DynamicConfigManager()
    return _config_manager

if __name__ == "__main__":
    # 测试配置管理器
    manager = get_config_manager()
    print("支持的提供商:", manager.get_provider_list())
    print("当前提供商:", manager.get_current_provider())
    print("当前配置:", manager.get_current_config())