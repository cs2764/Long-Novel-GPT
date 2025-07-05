from llm_api import ModelConfig

def get_model_config_from_provider_model(provider_model):
    """从provider/model格式获取模型配置，使用动态配置系统"""
    print(f"\n=== Getting Model Config ===")
    print(f"Provider Model: {provider_model}")
    
    try:
        # 使用动态配置管理器获取配置
        from core.dynamic_config_manager import get_config_manager
        
        config_manager = get_config_manager()
        
        # 解析 provider/model 格式
        if '/' in provider_model:
            provider_name, model_name = provider_model.split('/', 1)
        else:
            # 如果没有 '/'，使用当前提供商
            provider_name = config_manager.get_current_provider()
            model_name = provider_model
            
        print(f"Provider: {provider_name}, Model: {model_name}")
        
        # 获取提供商配置
        provider_config = config_manager.get_provider_config(provider_name)
        if not provider_config:
            error_msg = f"未找到提供商配置: {provider_name}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
        print(f"Provider config found: {provider_config}")
        
        # 构建模型配置
        model_config_dict = {
            'model': model_name,
            'api_key': provider_config.api_key,
            'max_tokens': 4096  # 默认值，可以根据需要调整
        }
        
        # 添加特定提供商的额外配置
        if provider_config.base_url:
            model_config_dict['base_url'] = provider_config.base_url
            
        # 处理特殊提供商的配置
        if provider_name == 'doubao':
            # Doubao需要endpoint_id配置
            # 这里可能需要从动态配置中获取endpoint_id映射
            # 暂时使用默认值或从原配置系统获取
            try:
                from config import API_SETTINGS
                if provider_name in API_SETTINGS:
                    old_config = API_SETTINGS[provider_name]
                    if 'endpoint_ids' in old_config and 'available_models' in old_config:
                        try:
                            model_index = old_config['available_models'].index(model_name)
                            if model_index < len(old_config['endpoint_ids']):
                                model_config_dict['endpoint_id'] = old_config['endpoint_ids'][model_index]
                        except (ValueError, IndexError):
                            print(f"⚠️ 无法为Doubao模型 {model_name} 找到endpoint_id")
            except ImportError:
                print(f"⚠️ 无法导入旧配置系统，Doubao配置可能不完整")
        
        print(f"Final model config dict: {model_config_dict}")
        
        model_config = ModelConfig(**model_config_dict)
        print(f"✅ Model config created successfully")
        return model_config
        
    except Exception as e:
        print(f"❌ Failed to get model config: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"获取模型配置失败: {str(e)}")
    finally:
        print(f"=== Model Config Creation Finished ===\n")