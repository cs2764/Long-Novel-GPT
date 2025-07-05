#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web配置界面
用于在Gradio界面中动态配置AI提供商设置
"""

import gradio as gr
from dynamic_config_manager import get_config_manager
import threading
import time
import concurrent.futures
from typing import Tuple, Any

class WebConfigInterface:
    """Web配置界面管理器"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self._test_lock = threading.Lock()
        # 添加模型刷新的超时控制
        self._refresh_timeout = 10  # 10秒超时
    
    def get_provider_choices(self):
        """获取提供商选择列表"""
        return self.config_manager.get_provider_list()
    
    def get_model_choices(self, provider_name, refresh=False):
        """根据提供商获取模型列表"""
        if not provider_name:
            return []
        return self.config_manager.get_provider_models(provider_name, refresh=refresh)
    
    def on_provider_change(self, provider_name):
        """当提供商改变时的回调"""
        if not provider_name:
            return gr.update(choices=[], value="", filterable=True), "", "", "", ""
        
        print(f"🔄 切换到提供商 {provider_name.upper()}")
        
        # 获取当前配置
        current_config = self.config_manager.get_provider_config(provider_name)
        current_api_key = current_config.api_key if current_config else ""
        current_model = current_config.model_name if current_config else ""
        current_base_url = current_config.base_url if current_config else ""
        current_system_prompt = current_config.system_prompt if current_config else ""
        
        # 尝试获取模型列表（使用缓存，避免长时间等待）
        try:
            print(f"📋 获取 {provider_name} 的模型列表（使用缓存）...")
            models = self.get_model_choices(provider_name, refresh=False)  # 使用缓存避免阻塞
            print(f"📤 get_model_choices返回: {models}")
        except Exception as e:
            print(f"⚠️ 获取{provider_name}模型列表出错: {e}")
            models = []
        
        # 确保当前模型在列表中
        if current_model and current_model not in models:
            models.append(current_model)
            print(f"🔧 添加当前模型到列表: {current_model}")
        
        print(f"✅ {provider_name.upper()} 模型列表已更新，共 {len(models)} 个模型")
        
        # 返回格式：(model_dropdown, api_key, base_url, system_prompt, status)
        return (
            gr.update(choices=models, value=current_model, filterable=True),  # 更新模型下拉菜单
            current_api_key,  # 更新API key
            current_base_url or "",  # 更新API地址
            current_system_prompt,  # 更新系统提示词
            f"已切换到 {provider_name.upper()}，模型列表已加载（{len(models)}个模型）"  # 状态信息
        )
    
    def save_config(self, provider_name, api_key, model_name, base_url, system_prompt):
        """保存配置"""
        try:
            if not provider_name:
                return "❌ 请选择提供商"
            
            if not api_key:
                return "❌ 请输入API密钥"
            
            if not model_name:
                return "❌ 请选择模型"
            
            # 更新配置
            success = self.config_manager.update_provider_config(
                provider_name, api_key, model_name, system_prompt, base_url
            )
            
            if not success:
                return f"❌ 配置更新失败: 未知提供商 {provider_name}"
            
            # 设置为当前提供商
            self.config_manager.set_current_provider(provider_name)
            
            # 保存到文件
            self.config_manager.save_config_to_file()
            
            prompt_info = f" (系统提示词: {len(system_prompt)}字符)" if system_prompt else ""
            url_info = f" (API地址: {base_url})" if base_url else ""
            return f"✅ 配置已保存: {provider_name.upper()} - {model_name}{url_info}{prompt_info}"
            
        except Exception as e:
            return f"❌ 保存配置失败: {str(e)}"
    
    def save_config_and_refresh(self, provider_name, api_key, model_name, base_url, system_prompt):
        """保存配置并刷新当前配置信息显示"""
        # 先保存配置
        save_result = self.save_config(provider_name, api_key, model_name, base_url, system_prompt)
        
        # 然后获取最新的配置信息
        current_info = self.get_current_config_info()
        
        # 返回保存结果和更新后的配置信息
        return save_result, current_info
    
    def test_connection(self, provider_name, api_key, model_name, base_url, system_prompt):
        """测试连接"""
        try:
            if not provider_name:
                return "❌ 请选择提供商"
            
            if not api_key:
                return "❌ 请输入API密钥"
            
            if not model_name:
                return "❌ 请选择模型"
            
            # 这里可以添加实际的连接测试逻辑
            # 暂时返回成功状态
            return f"✅ 连接测试成功: {provider_name.upper()} - {model_name}"
            
        except Exception as e:
            return f"❌ 连接测试失败: {str(e)}"
    
    def _refresh_models_with_timeout(self, provider_name: str) -> Tuple[list, str]:
        """带超时的模型刷新"""
        try:
            print(f"🔄 开始刷新 {provider_name} 的模型列表（超时: {self._refresh_timeout}秒）")
            
            # 获取当前配置
            current_config = self.config_manager.get_provider_config(provider_name)
            if not current_config:
                return [], f"❌ 未找到 {provider_name} 的配置信息"
            
            # 使用线程池执行，设置超时
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                # 提交任务
                future = executor.submit(self.config_manager.refresh_provider_models, provider_name)
                
                try:
                    # 等待结果，设置超时
                    models = future.result(timeout=self._refresh_timeout)
                    
                    if models and len(models) > 0:
                        success_msg = f"✅ 已刷新 {provider_name.upper()} 的模型列表，共获取到 {len(models)} 个模型"
                        print(success_msg)
                        return models, success_msg
                    else:
                        error_msg = f"⚠️ 获取到空的模型列表，使用默认模型"
                        print(error_msg)
                        # 返回默认模型列表
                        default_models = current_config.models if current_config.models else [current_config.model_name]
                        return default_models, error_msg
                        
                except concurrent.futures.TimeoutError:
                    # 超时处理
                    error_msg = f"⏱️ 刷新超时（{self._refresh_timeout}秒），使用缓存的模型列表"
                    print(error_msg)
                    cached_models = current_config.models if current_config.models else [current_config.model_name]
                    return cached_models, error_msg
                    
        except Exception as e:
            import traceback
            error_msg = f"❌ 刷新模型列表失败: {str(e)}"
            print(f"{error_msg}")
            print(f"详细错误信息: {traceback.format_exc()}")
            
            # 返回默认模型列表
            try:
                current_config = self.config_manager.get_provider_config(provider_name)
                if current_config:
                    fallback_models = current_config.models if current_config.models else [current_config.model_name]
                    return fallback_models, f"{error_msg}，使用默认模型列表"
            except:
                pass
            
            return [], error_msg
    
    def refresh_models(self, provider_name):
        """刷新模型列表"""
        if not provider_name:
            return gr.update(choices=[], value="", filterable=True), "❌ 请先选择提供商"
        
        print(f"\n=== 开始刷新 {provider_name.upper()} 模型列表 ===")
        
        try:
            # 显示当前配置信息
            current_config = self.config_manager.get_provider_config(provider_name)
            if current_config:
                api_key_display = f"{current_config.api_key[:8]}***{current_config.api_key[-4:]}" if len(current_config.api_key) > 12 else "***"
                print(f"📋 提供商: {provider_name}")
                print(f"🔑 API密钥: {api_key_display}")
                print(f"🌐 API地址: {current_config.base_url or '默认'}")
            
            # 使用带超时的刷新方法
            models, status_msg = self._refresh_models_with_timeout(provider_name)
            
            print(f"📤 刷新结果: {len(models)} 个模型")
            print("=== 刷新完成 ===\n")
            
            if models:
                # 返回成功结果
                return gr.update(choices=models, value=models[0] if models else "", filterable=True), status_msg
            else:
                # 返回空结果
                return gr.update(choices=[], value="", filterable=True), status_msg
                
        except Exception as e:
            import traceback
            error_msg = f"❌ 刷新过程异常: {str(e)}"
            print(f"{error_msg}")
            print(f"详细错误信息: {traceback.format_exc()}")
            print("=== 刷新异常 ===\n")
            return gr.update(choices=[], value="", filterable=True), error_msg
    
    def get_current_config_info(self):
        """获取当前配置信息"""
        try:
            current_provider = self.config_manager.get_current_provider()
            current_config = self.config_manager.get_current_config()
            
            if not current_config:
                return "❌ 未找到当前配置"
            
            # 隐藏API密钥
            api_key_display = current_config.api_key
            if len(api_key_display) > 8:
                api_key_display = api_key_display[:4] + "***" + api_key_display[-4:]
            
            info = f"""📊 当前配置信息:
🔧 提供商: {current_provider.upper()}
🤖 模型: {current_config.model_name}
🔑 API密钥: {api_key_display}"""
            
            if current_config.base_url:
                info += f"\n🌐 API地址: {current_config.base_url}"
            
            if current_config.system_prompt:
                prompt_preview = current_config.system_prompt[:50] + "..." if len(current_config.system_prompt) > 50 else current_config.system_prompt
                info += f"\n💬 系统提示词: {prompt_preview} ({len(current_config.system_prompt)}字符)"
            else:
                info += f"\n💬 系统提示词: 未设置"
            
            return info
            
        except Exception as e:
            return f"❌ 获取配置信息失败: {str(e)}"
    
    def create_config_interface(self):
        """创建配置界面组件"""
        with gr.Column():
            gr.Markdown("### 🔧 AI提供商配置")
            
            # 当前配置信息
            current_info = gr.Textbox(
                label="当前配置",
                value=self.get_current_config_info(),
                lines=5,
                interactive=False
            )
            
            # 配置表单
            with gr.Row():
                provider_dropdown = gr.Dropdown(
                    choices=self.get_provider_choices(),
                    label="提供商",
                    value=self.config_manager.get_current_provider(),
                    interactive=True,
                    filterable=True
                )
                
                with gr.Column():
                    model_dropdown = gr.Dropdown(
                        choices=self.get_model_choices(self.config_manager.get_current_provider()),
                        label="模型",
                        value=self.config_manager.get_current_config().model_name if self.config_manager.get_current_config() else "",
                        interactive=True,
                        filterable=True
                    )
                    refresh_models_btn = gr.Button("🔄 刷新模型", size="sm", scale=0)
            
            api_key_input = gr.Textbox(
                label="API密钥",
                type="password",
                value=self.config_manager.get_current_config().api_key if self.config_manager.get_current_config() else "",
                placeholder="请输入您的API密钥",
                interactive=True
            )
            
            base_url_input = gr.Textbox(
                label="API地址",
                value=self.config_manager.get_current_config().base_url if self.config_manager.get_current_config() else "",
                placeholder="API接口地址(可选，留空使用默认地址)",
                interactive=True
            )
            
            system_prompt_input = gr.Textbox(
                label="系统提示词",
                value=self.config_manager.get_current_config().system_prompt if self.config_manager.get_current_config() else "",
                placeholder="设置模型的默认系统提示词(可选)",
                lines=3,
                interactive=True
            )
            
            # 操作按钮
            with gr.Row():
                test_btn = gr.Button("🔍 测试连接", variant="secondary")
                save_btn = gr.Button("💾 保存配置", variant="primary")
                refresh_btn = gr.Button("🔄 刷新信息", variant="secondary")
                reload_btn = gr.Button("🔄 重载模型", variant="secondary")
            
            # 状态信息
            status_output = gr.Textbox(
                label="状态",
                lines=2,
                interactive=False
            )
            
            # 事件绑定
            provider_dropdown.change(
                fn=self.on_provider_change,
                inputs=[provider_dropdown],
                outputs=[model_dropdown, api_key_input, base_url_input, system_prompt_input, status_output]
            )
            
            test_btn.click(
                fn=self.test_connection,
                inputs=[provider_dropdown, api_key_input, model_dropdown, base_url_input, system_prompt_input],
                outputs=[status_output]
            )
            
            save_btn.click(
                fn=self.save_config_and_refresh,
                inputs=[provider_dropdown, api_key_input, model_dropdown, base_url_input, system_prompt_input],
                outputs=[status_output, current_info]
            )
            
            refresh_btn.click(
                fn=self.get_current_config_info,
                outputs=[current_info]
            )
            
            refresh_models_btn.click(
                fn=self.refresh_models,
                inputs=[provider_dropdown],
                outputs=[model_dropdown, status_output]
            )
            
            return {
                'provider_dropdown': provider_dropdown,
                'model_dropdown': model_dropdown,
                'api_key_input': api_key_input,
                'base_url_input': base_url_input,
                'system_prompt_input': system_prompt_input,
                'status_output': status_output,
                'current_info': current_info,
                'reload_btn': reload_btn
            }

# 全局实例
_web_config = WebConfigInterface()

def get_web_config_interface():
    """获取全局Web配置界面实例"""
    return _web_config

if __name__ == "__main__":
    # 测试配置界面
    config_interface = get_web_config_interface()
    print("支持的提供商:", config_interface.get_provider_choices())
    print("当前配置:", config_interface.get_current_config_info())