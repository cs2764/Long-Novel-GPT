#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器
负责加载和管理AI小说生成器的配置信息
"""

import os
import sys
from typing import Dict, Any, Optional

def load_config(allow_incomplete: bool = False) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        allow_incomplete: 是否允许不完整的配置（用于Web界面启动）
    
    Returns:
        Dict[str, Any]: 配置字典
        
    Raises:
        SystemExit: 当配置文件不存在或配置错误时（除非allow_incomplete=True）
    """
    config_path = "config.py"
    template_path = "config_template.py"
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        if allow_incomplete:
            print("⚠️  配置文件不存在，返回默认配置")
            return {
                'provider': 'deepseek',
                'config': {'api_key': '', 'model_name': 'deepseek-chat'},
                'novel_settings': {},
                'temperature_settings': {},
                'network_settings': {},
                'all_configs': {},
                'incomplete': True
            }
        else:
            print("❌ 配置文件不存在！")
            print(f"📋 请复制 {template_path} 为 {config_path} 并填入您的配置信息")
            print("\n快速设置步骤:")
            print(f"1. 复制文件: cp {template_path} {config_path}")
            print(f"2. 编辑文件: 填入您的API密钥和设置")
            print(f"3. 重新运行程序")
            sys.exit(1)
    
    # 动态导入配置模块
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # 验证必要的配置项
        required_configs = [
            'CURRENT_PROVIDER',
            'DEEPSEEK_CONFIG',
            'ALI_CONFIG', 
            'ZHIPU_CONFIG',
            'LMSTUDIO_CONFIG',
            'GEMINI_CONFIG',
            'OPENROUTER_CONFIG',
            'CLAUDE_CONFIG'
        ]
        
        for config_name in required_configs:
            if not hasattr(config_module, config_name):
                if allow_incomplete:
                    print(f"⚠️  配置文件缺少配置项: {config_name}，使用默认值")
                    setattr(config_module, config_name, {})
                else:
                    print(f"❌ 配置文件缺少必要配置项: {config_name}")
                    print(f"📋 请参考 {template_path} 补充配置")
                    sys.exit(1)
        
        # 验证当前提供商设置
        provider = config_module.CURRENT_PROVIDER
        valid_providers = ["deepseek", "ali", "zhipu", "lmstudio", "gemini", "openrouter", "claude"]
        
        if provider not in valid_providers:
            if allow_incomplete:
                print(f"⚠️  无效的AI提供商: {provider}，使用默认值: deepseek")
                provider = "deepseek"
                config_module.CURRENT_PROVIDER = provider
            else:
                print(f"❌ 无效的AI提供商: {provider}")
                print(f"📋 请选择: {', '.join(valid_providers)}")
                sys.exit(1)
            
        # 验证对应提供商的API密钥
        provider_configs = {
            "deepseek": config_module.DEEPSEEK_CONFIG,
            "ali": config_module.ALI_CONFIG,
            "zhipu": config_module.ZHIPU_CONFIG,
            "lmstudio": config_module.LMSTUDIO_CONFIG,
            "gemini": config_module.GEMINI_CONFIG,
            "openrouter": config_module.OPENROUTER_CONFIG,
            "claude": config_module.CLAUDE_CONFIG
        }
        
        current_config = provider_configs[provider]
        api_key = current_config.get("api_key", "")
        
        if provider != "lmstudio" and (not api_key or "your-" in api_key.lower()):
            if allow_incomplete:
                print(f"⚠️  {provider.upper()}_CONFIG 的 api_key 未设置，将在Web界面中配置")
            else:
                print(f"❌ 请在配置文件中设置 {provider.upper()}_CONFIG 的 api_key")
                print(f"📋 编辑 {config_path} 文件，填入您的API密钥")
                sys.exit(1)
        
        if not allow_incomplete or (provider == "lmstudio" or (api_key and "your-" not in api_key.lower())):
            print(f"✅ 配置加载成功，当前使用: {provider.upper()}")
        
        return {
            'provider': provider,
            'config': current_config,
            'novel_settings': getattr(config_module, 'NOVEL_SETTINGS', {}),
            'temperature_settings': getattr(config_module, 'TEMPERATURE_SETTINGS', {}),
            'network_settings': getattr(config_module, 'NETWORK_SETTINGS', {}),
            'all_configs': provider_configs,
            'incomplete': allow_incomplete and (provider != "lmstudio" and (not api_key or "your-" in api_key.lower()))
        }
        
    except Exception as e:
        if allow_incomplete:
            print(f"⚠️  配置文件加载失败: {e}，返回默认配置")
            return {
                'provider': 'deepseek',
                'config': {'api_key': '', 'model_name': 'deepseek-chat'},
                'novel_settings': {},
                'temperature_settings': {},
                'network_settings': {},
                'all_configs': {},
                'incomplete': True
            }
        else:
            print(f"❌ 配置文件加载失败: {e}")
            print(f"📋 请检查 {config_path} 文件格式是否正确")
            print(f"💡 可以删除 {config_path} 并重新复制 {template_path}")
            sys.exit(1)


def get_chatllm(allow_incomplete: bool = False):
    """
    根据配置获取ChatLLM实例（优先使用动态配置）
    
    Args:
        allow_incomplete: 是否允许不完整的配置
    
    Returns:
        Callable: ChatLLM函数
    """
    # Try to import AI modules
    try:
        from uniai import (
            aliChatLLM, deepseekChatLLM, zhipuChatLLM, lmstudioChatLLM,
            geminiChatLLM, openrouterChatLLM, claudeChatLLM
        )
    except ImportError as import_err:
        if allow_incomplete:
            print(f"⚠️  AI模块导入失败: {import_err}，返回虚拟函数")
            def dummy_chatllm(*args, **kwargs):
                yield {"content": "AI模块未安装，请先安装依赖: pip install -r requirements.txt", "total_tokens": 0}
            return dummy_chatllm
        else:
            raise
    
    # 优先使用动态配置
    try:
        from dynamic_config_manager import get_config_manager
        config_manager = get_config_manager()
        
        provider = config_manager.get_current_provider()
        current_config = config_manager.get_current_config()
        
        # 检查动态配置是否有效
        if current_config and current_config.api_key:
            # LM Studio不需要真实API密钥
            if provider == "lmstudio" or "your-" not in current_config.api_key.lower():
                print(f"✅ 使用动态配置，当前提供商: {provider.upper()}")
                provider_config = {
                    'api_key': current_config.api_key,
                    'model_name': current_config.model_name,
                    'base_url': current_config.base_url,
                    'system_prompt': current_config.system_prompt
                }
            else:
                # 动态配置无效，回退到静态配置
                config = load_config(allow_incomplete=allow_incomplete)
                provider = config['provider']
                provider_config = config['config']
                
                # 如果静态配置也不完整，返回错误函数
                if config.get('incomplete', False):
                    def dummy_chatllm(*args, **kwargs):
                        yield {"content": "请先在配置界面设置API密钥", "total_tokens": 0}
                    return dummy_chatllm
        else:
            # 没有动态配置，使用静态配置
            config = load_config(allow_incomplete=allow_incomplete)
            provider = config['provider']
            provider_config = config['config']
            
            # 如果静态配置不完整，返回错误函数
            if config.get('incomplete', False):
                def dummy_chatllm(*args, **kwargs):
                    yield {"content": "请先在配置界面设置API密钥", "total_tokens": 0}
                return dummy_chatllm
                
    except Exception as e:
        print(f"⚠️  动态配置加载失败: {e}，回退到静态配置")
        config = load_config(allow_incomplete=allow_incomplete)
        provider = config['provider']
        provider_config = config['config']
        
        # If config is incomplete, return a dummy function
        if config.get('incomplete', False):
            def dummy_chatllm(*args, **kwargs):
                yield {"content": "请先在配置界面设置API密钥", "total_tokens": 0}
            return dummy_chatllm
    
    try:
        if provider == "deepseek":
            return deepseekChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "ali":
            return aliChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "zhipu":
            return zhipuChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "lmstudio":
            return lmstudioChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                base_url=provider_config['base_url'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "gemini":
            return geminiChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "openrouter":
            return openrouterChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        elif provider == "claude":
            return claudeChatLLM(
                model_name=provider_config['model_name'],
                api_key=provider_config['api_key'],
                system_prompt=provider_config.get('system_prompt', '')
            )
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
            
    except Exception as e:
        if allow_incomplete:
            print(f"⚠️  初始化AI提供商失败: {e}，返回虚拟函数")
            def dummy_chatllm(*args, **kwargs):
                yield {"content": f"AI提供商初始化失败: {e}", "total_tokens": 0}
            return dummy_chatllm
        else:
            print(f"❌ 初始化AI提供商失败: {e}")
            print(f"📋 请检查 {provider.upper()}_CONFIG 配置是否正确")
            sys.exit(1)


def update_aign_settings(aign_instance, allow_incomplete: bool = False):
    """
    根据配置更新AIGN实例的设置
    
    Args:
        aign_instance: AIGN实例
        allow_incomplete: 是否允许不完整的配置
    """
    config = load_config(allow_incomplete=allow_incomplete)
    
    # 应用小说设置
    novel_settings = config.get('novel_settings', {})
    if novel_settings:
        aign_instance.target_chapter_count = novel_settings.get('default_chapters', 20)
        aign_instance.enable_chapters = novel_settings.get('enable_chapters', True)
        aign_instance.enable_ending = novel_settings.get('enable_ending', True)
    
    # 应用温度设置
    temp_settings = config.get('temperature_settings', {})
    if temp_settings:
        aign_instance.novel_outline_writer.temperature = temp_settings.get('outline_writer', 0.98)
        aign_instance.novel_beginning_writer.temperature = temp_settings.get('beginning_writer', 0.80)
        aign_instance.novel_writer.temperature = temp_settings.get('novel_writer', 0.81)
        aign_instance.novel_embellisher.temperature = temp_settings.get('embellisher', 0.92)
        aign_instance.memory_maker.temperature = temp_settings.get('memory_maker', 0.66)
        aign_instance.title_generator.temperature = temp_settings.get('title_generator', 0.8)
        aign_instance.ending_writer.temperature = temp_settings.get('ending_writer', 0.85)


def print_config_info():
    """打印配置信息（不包含敏感信息）"""
    config = load_config()
    provider = config['provider']
    provider_config = config['config']
    
    print("=" * 50)
    print("🔧 当前配置信息")
    print("=" * 50)
    print(f"📡 AI提供商: {provider.upper()}")
    print(f"🤖 模型名称: {provider_config['model_name']}")
    print(f"🔑 API密钥: {'*' * (len(provider_config['api_key']) - 4)}{provider_config['api_key'][-4:] if len(provider_config['api_key']) > 4 else '****'}")
    
    if provider_config.get('base_url'):
        print(f"🌐 API地址: {provider_config['base_url']}")
    
    novel_settings = config.get('novel_settings', {})
    if novel_settings:
        print(f"📚 默认章节数: {novel_settings.get('default_chapters', 20)}")
        print(f"📖 章节标题: {'启用' if novel_settings.get('enable_chapters', True) else '禁用'}")
        print(f"🎯 智能结尾: {'启用' if novel_settings.get('enable_ending', True) else '禁用'}")
    
    print("=" * 50)


if __name__ == "__main__":
    print_config_info()