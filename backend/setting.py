from flask import Blueprint, jsonify, request

setting_bp = Blueprint('setting', __name__)

@setting_bp.route('/setting', methods=['GET'])
def get_settings():
    """Get current settings and models"""
    from config import API_SETTINGS, DEFAULT_MAIN_MODEL, DEFAULT_SUB_MODEL, MAX_THREAD_NUM, MAX_NOVEL_SUMMARY_LENGTH
    
    # Get models grouped by provider
    models = {provider: config['available_models'] for provider, config in API_SETTINGS.items() if 'available_models' in config}
    
    # Combine all settings
    settings = {
        'models': models,
        'MAIN_MODEL': DEFAULT_MAIN_MODEL,
        'SUB_MODEL': DEFAULT_SUB_MODEL,
        'MAX_THREAD_NUM': MAX_THREAD_NUM,
        'MAX_NOVEL_SUMMARY_LENGTH': MAX_NOVEL_SUMMARY_LENGTH,
    }
    return jsonify(settings)

@setting_bp.route('/test_model', methods=['POST'])
def test_model():
    """Test if a model configuration works"""
    import traceback
    
    print(f"\n=== Testing Model via /test_model endpoint ===")
    
    try:
        data = request.get_json()
        provider_model = data.get('provider_model')
        
        print(f"Provider model: {provider_model}")
        
        if not provider_model:
            error_msg = "provider_model参数不能为空"
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # 使用动态配置管理器获取模型配置
        from core.dynamic_config_manager import get_config_manager
        from llm_api import ModelConfig
        
        config_manager = get_config_manager()
        
        # 解析 provider/model 格式
        if '/' in provider_model:
            provider_name, model_name = provider_model.split('/', 1)
        else:
            # 如果没有 '/'，尝试查找当前提供商
            provider_name = config_manager.get_current_provider()
            model_name = provider_model
            
        print(f"Provider: {provider_name}, Model: {model_name}")
        
        # 获取提供商配置
        provider_config = config_manager.get_provider_config(provider_name)
        if not provider_config:
            error_msg = f"未找到提供商配置: {provider_name}"
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
            
        # 构建模型配置
        model_config = ModelConfig(
            model=model_name,
            api_key=provider_config.api_key,
            max_tokens=100  # 测试时使用小的token数
        )
        
        # 添加特定提供商的额外配置
        if provider_config.base_url:
            model_config['base_url'] = provider_config.base_url
            
        print(f"Model config: {dict(model_config)}")
        
        from llm_api import test_stream_chat
        response = None
        test_content = ""
        
        print(f"🧪 Starting model test...")
        
        for msg in test_stream_chat(model_config):
            response = msg
            test_content += msg
            if len(test_content) > 100:  # 限制测试响应长度
                break
            
        print(f"✅ Model test completed successfully")
        print(f"Response: {test_content[:100]}...")
        
        return jsonify({
            'success': True,
            'response': test_content
        })
        
    except Exception as e:
        error_msg = f"模型测试失败: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
    finally:
        print(f"=== Model Test Finished ===\n")
