#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态配置管理器
负责运行时动态管理AI提供商配置，支持通过Web界面实时更新设置
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
import time
try:
    from model_fetcher import ModelFetcher
except ImportError:
    ModelFetcher = None

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
        self._config_lock = threading.RLock()  # 使用RLock支持重入
        self._current_provider = "deepseek"
        self._providers = {}
        self._load_default_configs()
        # 尝试从文件加载配置
        self.load_config_from_file()
    
    def _load_default_configs(self):
        """加载默认配置"""
        # 默认支持的提供商和模型
        default_configs = {
            "deepseek": ProviderConfig(
                name="deepseek",
                api_key="your-deepseek-api-key-here",
                model_name="deepseek-chat",
                base_url="https://api.deepseek.com",
                models=["deepseek-chat", "deepseek-coder"]
            ),
            "ali": ProviderConfig(
                name="ali",
                api_key="your-ali-api-key-here", 
                model_name="qwen-long",
                base_url=None,
                models=["qwen-long", "qwen-plus", "qwen-turbo", "qwen-max"]
            ),
            "zhipu": ProviderConfig(
                name="zhipu",
                api_key="your-zhipu-api-key-here",
                model_name="glm-4",
                base_url=None,
                models=["glm-4", "glm-3-turbo", "glm-4-flash"]
            ),
            "lmstudio": ProviderConfig(
                name="lmstudio",
                api_key="lm-studio",
                model_name="your-local-model-name",
                base_url="http://localhost:1234/v1",
                models=["your-local-model-name"]
            ),
            "gemini": ProviderConfig(
                name="gemini",
                api_key="your-gemini-api-key-here",
                model_name="gemini-pro",
                base_url=None,
                models=["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"]
            ),
            "openrouter": ProviderConfig(
                name="openrouter",
                api_key="your-openrouter-api-key-here",
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
                api_key="your-claude-api-key-here",
                model_name="claude-3-sonnet-20240229",
                base_url="https://api.anthropic.com",
                models=[
                    "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
                    "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"
                ]
            )
        }
        
        with self._config_lock:
            self._providers = default_configs
    
    def get_provider_list(self) -> List[str]:
        """获取所有支持的提供商列表"""
        with self._config_lock:
            return list(self._providers.keys())
    
    def get_provider_models(self, provider_name: str, refresh: bool = False) -> List[str]:
        """获取指定提供商的模型列表"""
        # 首先获取基本信息（无锁获取，避免长时间阻塞）
        config = None
        try:
            with self._config_lock:
                if provider_name not in self._providers:
                    print(f"❌ 提供商 {provider_name} 不存在于配置中")
                    return []
                config = self._providers[provider_name]
                
            print(f"📋 获取 {provider_name} 模型列表，当前有 {len(config.models)} 个模型，refresh={refresh}")
            
            # 如果需要刷新或者模型列表为空，尝试从API获取
            if refresh or not config.models:
                print(f"🔄 需要刷新模型列表: refresh={refresh}, 当前模型数量={len(config.models)}")
                
                if ModelFetcher:
                    try:
                        print(f"🔧 使用ModelFetcher获取 {provider_name} 的模型列表")
                        # 在锁外执行网络请求，避免阻塞其他操作
                        fresh_models = ModelFetcher.fetch_models(
                            provider_name, 
                            config.api_key, 
                            config.base_url
                        )
                        print(f"📥 ModelFetcher返回 {len(fresh_models)} 个模型: {fresh_models}")
                        
                        if fresh_models:
                            # 只在更新配置时使用锁
                            with self._config_lock:
                                self._providers[provider_name].models = fresh_models
                                print(f"💾 更新 {provider_name} 配置中的模型列表")
                            # 保存更新后的配置
                            self.save_config_to_file()
                            result = fresh_models.copy()
                        else:
                            print(f"⚠️ ModelFetcher返回空列表，保持原有模型列表")
                            result = config.models.copy()
                    except Exception as e:
                        import traceback
                        print(f"❌ 刷新{provider_name}模型列表失败: {e}")
                        print(f"详细错误: {traceback.format_exc()}")
                        result = config.models.copy()
                else:
                    print("❌ ModelFetcher模块未找到，使用默认模型列表")
                    result = config.models.copy()
            else:
                result = config.models.copy()
            
            print(f"📤 返回 {provider_name} 模型列表，共 {len(result)} 个模型")
            return result
            
        except Exception as e:
            print(f"❌ 获取{provider_name}模型列表时发生异常: {e}")
            return []
    
    def refresh_provider_models(self, provider_name: str) -> List[str]:
        """强制刷新指定提供商的模型列表"""
        return self.get_provider_models(provider_name, refresh=True)
    
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
    
    def update_provider_config(self, provider_name: str, api_key: str, model_name: str, system_prompt: str = "", base_url: str = None) -> bool:
        """更新提供商配置"""
        with self._config_lock:
            if provider_name not in self._providers:
                return False
            
            config = self._providers[provider_name]
            config.api_key = api_key
            config.model_name = model_name
            config.system_prompt = system_prompt
            if base_url is not None:
                config.base_url = base_url
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
    
    def get_chatllm_instance(self):
        """获取当前配置的ChatLLM实例"""
        current_config = self.get_current_config()
        if not current_config:
            raise ValueError("No current provider configured")
        
        if not self.validate_config(self._current_provider):
            raise ValueError(f"Invalid configuration for {self._current_provider}")
        
        # 动态导入对应的ChatLLM函数
        provider_name = self._current_provider
        
        if provider_name == "deepseek":
            from uniai.deepseekAI import deepseekChatLLM
            return deepseekChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "ali":
            from uniai.aliAI import aliChatLLM
            return aliChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "zhipu":
            from uniai.zhipuAI import zhipuChatLLM
            return zhipuChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "lmstudio":
            from uniai.lmstudioAI import lmstudioChatLLM
            return lmstudioChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                base_url=current_config.base_url,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "gemini":
            from uniai.geminiAI import geminiChatLLM
            return geminiChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "openrouter":
            from uniai.openrouterAI import openrouterChatLLM
            return openrouterChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                base_url=current_config.base_url,
                system_prompt=current_config.system_prompt
            )
        elif provider_name == "claude":
            from uniai.claudeAI import claudeChatLLM
            return claudeChatLLM(
                model_name=current_config.model_name,
                api_key=current_config.api_key,
                system_prompt=current_config.system_prompt
            )
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

# 全局配置管理器实例
_config_manager = None
_config_lock = threading.Lock()

def get_config_manager() -> DynamicConfigManager:
    """获取全局配置管理器实例（单例模式）"""
    global _config_manager
    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:  # 双重检查
                _config_manager = DynamicConfigManager()
    return _config_manager

# 兼容性函数
def get_dynamic_chatllm():
    """获取动态配置的ChatLLM实例"""
    return _config_manager.get_chatllm_instance()

if __name__ == "__main__":
    # 测试配置管理器
    manager = get_config_manager()
    print("支持的提供商:", manager.get_provider_list())
    print("当前提供商:", manager.get_current_provider())
    print("当前配置:", manager.get_current_config())