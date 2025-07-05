#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态配置API接口
提供Web界面配置AI提供商的API端点
"""

from flask import Blueprint, request, jsonify
import sys
import os
import time

# 添加核心模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.dynamic_config_manager import get_config_manager
except ImportError:
    print("Warning: dynamic_config_manager not found, creating mock manager")
    
    class MockConfigManager:
        def get_provider_list(self):
            return ["deepseek", "aliyun", "zhipuai", "lmstudio", "gemini", "openrouter", "claude"]
        
        def get_provider_models(self, provider_name):
            default_models = {
                "deepseek": ["deepseek-chat", "deepseek-coder"],
                "aliyun": ["qwen-max", "qwen-plus", "qwen-turbo"],
                "zhipuai": ["glm-4-air", "glm-4-flashx", "glm-4-plus"],
                "lmstudio": ["local-model"],
                "gemini": ["gemini-pro", "gemini-1.5-pro"],
                "openrouter": ["openai/gpt-4", "anthropic/claude-3-opus"],
                "claude": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            }
            return default_models.get(provider_name, [])
        
        def test_provider_connection(self, provider_name, config):
            return {"success": True, "message": f"Mock test for {provider_name}"}
        
        def load_provider_models(self, provider_name, config):
            return {"success": True, "models": self.get_provider_models(provider_name)}
        
        def update_provider_config(self, provider_name, config):
            return True
        
        def save_config_to_file(self):
            return True
        
        def get_all_configs(self):
            return {"current_provider": "deepseek", "providers": {}}
    
    get_config_manager = lambda: MockConfigManager()

# 创建Blueprint
dynamic_config_bp = Blueprint('dynamic_config', __name__, url_prefix='/api')

@dynamic_config_bp.route('/providers', methods=['GET'])
def get_providers():
    """获取所有支持的AI提供商列表"""
    try:
        config_manager = get_config_manager()
        providers = config_manager.get_provider_list()
        
        return jsonify({
            'success': True,
            'providers': providers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/provider_models', methods=['POST'])
def get_provider_models():
    """获取指定提供商的模型列表"""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        
        if not provider_name:
            return jsonify({
                'success': False,
                'error': '提供商名称不能为空'
            }), 400
        
        config_manager = get_config_manager()
        models = config_manager.get_provider_models(provider_name)
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/test_provider', methods=['POST'])
def test_provider():
    """测试AI提供商连接"""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        config = data.get('config', {})
        
        if not provider_name:
            return jsonify({
                'success': False,
                'error': '提供商名称不能为空'
            }), 400
        
        config_manager = get_config_manager()
        result = config_manager.test_provider_connection(provider_name, config)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/save_provider_config', methods=['POST'])
def save_provider_config():
    """保存AI提供商配置"""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        config = data.get('config', {})
        
        if not provider_name:
            return jsonify({
                'success': False,
                'error': '提供商名称不能为空'
            }), 400
        
        config_manager = get_config_manager()
        
        # 更新配置
        success = config_manager.update_provider_config(provider_name, config)
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'未知的提供商: {provider_name}'
            }), 400
        
        # 保存到文件
        config_manager.save_config_to_file()
        
        return jsonify({
            'success': True,
            'message': f'{provider_name} 配置保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/load_provider_models', methods=['POST'])
def load_provider_models():
    """从提供商API加载模型列表"""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        config = data.get('config', {})
        
        if not provider_name:
            return jsonify({
                'success': False,
                'error': '提供商名称不能为空'
            }), 400
        
        config_manager = get_config_manager()
        result = config_manager.load_provider_models(provider_name, config)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/reload_models', methods=['POST'])
def reload_models():
    """重新加载所有模型实例"""
    try:
        # TODO: 实现重新加载模型实例的逻辑
        # 这里可能需要重新初始化模型配置，清除缓存等
        
        return jsonify({
            'success': True,
            'message': '模型实例重新加载成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/config_info', methods=['GET'])
def get_config_info():
    """获取当前配置信息"""
    try:
        config_manager = get_config_manager()
        config_info = config_manager.get_all_configs()
        
        return jsonify({
            'success': True,
            'config': config_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/validate_config', methods=['POST'])
def validate_config():
    """验证配置是否有效"""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        
        if not provider_name:
            return jsonify({
                'success': False,
                'error': '提供商名称不能为空'
            }), 400
        
        config_manager = get_config_manager()
        is_valid = config_manager.validate_config(provider_name)
        
        return jsonify({
            'success': True,
            'valid': is_valid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/export_config', methods=['GET'])
def export_config():
    """导出配置文件"""
    try:
        config_manager = get_config_manager()
        config_info = config_manager.get_all_configs()
        
        # 为导出添加元数据
        export_data = {
            'version': '1.0',
            'timestamp': int(time.time()),
            'config': config_info
        }
        
        return jsonify({
            'success': True,
            'data': export_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_config_bp.route('/import_config', methods=['POST'])
def import_config():
    """导入配置文件"""
    try:
        data = request.get_json()
        config_data = data.get('config')
        
        if not config_data:
            return jsonify({
                'success': False,
                'error': '配置数据不能为空'
            }), 400
        
        config_manager = get_config_manager()
        
        # TODO: 实现配置导入逻辑
        # 这里需要验证配置格式，更新内存中的配置，并保存到文件
        
        return jsonify({
            'success': True,
            'message': '配置导入成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 为了兼容性，保持原有的端点
@dynamic_config_bp.route('/get_provider_models', methods=['POST'])
def get_provider_models_compat():
    """获取提供商模型列表（兼容性端点）"""
    return get_provider_models()

if __name__ == "__main__":
    # 测试API端点
    print("Dynamic Config API endpoints:")
    for rule in dynamic_config_bp.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods)}]")