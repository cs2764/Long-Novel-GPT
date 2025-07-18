from zhipuai import ZhipuAI
from .chat_messages import ChatMessages

# Pricing
# https://open.bigmodel.cn/pricing
# GLM-4-Plus 0.05￥/1000 tokens, GLM-4-Air 0.001￥/1000 tokens, GLM-4-FlashX 0.0001￥/1000 tokens, , GLM-4-Flash 0￥/1000 tokens

# Models
# https://bigmodel.cn/dev/howuse/model
# glm-4-plus、glm-4-air、 glm-4-flashx 、 glm-4-flash



zhipuai_model_config = {
    "glm-4-plus": {
        "Pricing": (0.05, 0.05),
        "currency_symbol": '￥',
    },
    "glm-4-air": {
        "Pricing": (0.001, 0.001),
        "currency_symbol": '￥',
    },
    "glm-4-flashx": {
        "Pricing": (0.0001, 0.0001),
        "currency_symbol": '￥',
    },
    "glm-4-flash": {
        "Pricing": (0, 0),
        "currency_symbol": '￥',
    },
}

def stream_chat_with_zhipuai(messages, model='glm-4-flash', response_json=False, api_key=None, max_tokens=4_096):
    import traceback
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
    
    if api_key is None:
        error_msg = '未提供有效的 api_key！'
        print(f"❌ API Key Error: {error_msg}")
        raise Exception(error_msg)
    
    try:
        print(f"✅ Creating ZhipuAI client...")
        client = ZhipuAI(api_key=api_key)
        print(f"✅ ZhipuAI client created successfully")
        
        request_params = {
            'model': model,
            'messages': messages,
            'stream': True,
            'max_tokens': max_tokens
        }
        
        print(f"\n🌐 === ZhipuAI API Request Details ===")
        print(f"Model: {model}")
        print(f"Messages Count: {len(messages)}")
        print(f"Stream: True")
        print(f"Max Tokens: {max_tokens}")
        safe_messages = [
            {**msg, 'content': msg['content'][:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')}
            for msg in messages
        ]
        print(f"Request Messages: {json.dumps(safe_messages, indent=2, ensure_ascii=False)}")
        print(f"=== End ZhipuAI Request Details ===\n")
        
        print(f"🚀 Sending request to ZhipuAI API")
        start_time = time.time()
        
        response = client.chat.completions.create(**request_params)
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s, starting to stream response")
        
        messages.append({'role': 'assistant', 'content': ''})
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in response:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:  # Log first few chunks for debugging
                print(f"📦 Chunk #{chunk_count}: {str(chunk)[:200]}...")
            
            messages[-1]['content'] += chunk.choices[0].delta.content or ''
            
            # 对内容进行思考过程过滤（处理 <think> </think> 等标签）
            from prompts.prompt_utils import filter_thinking_process
            filtered_content = filter_thinking_process(messages[-1]['content'])
            messages[-1]['content'] = filtered_content
            
            yield messages
        
        total_time = time.time() - start_time
        print(f"✅ ZhipuAI API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        return messages
        
    except Exception as e:
        print(f"❌ ZhipuAI API Call Failed: {type(e).__name__}: {str(e)}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        
        # 尝试提取更详细的错误信息
        if hasattr(e, 'response'):
            print(f"🔍 HTTP Response Details:")
            print(f"  Status Code: {getattr(e.response, 'status_code', 'Unknown')}")
            print(f"  Headers: {dict(getattr(e.response, 'headers', {}))}")
            try:
                response_text = e.response.text if hasattr(e.response, 'text') else str(e.response)
                print(f"  Response Body: {response_text[:1000]}...")
            except:
                print(f"  Response Body: Unable to read")
        
        # 重新抛出异常，但包含更多信息
        raise Exception(f"ZhipuAI API调用失败 - {type(e).__name__}: {str(e)}")
        
    finally:
        print(f"=== ZhipuAI API Call Finished ===\n")

if __name__ == '__main__':
    pass