from openai import OpenAI
from .chat_messages import ChatMessages

doubao_model_config = {
    "doubao-lite-32k":{
        "Pricing": (0.0003, 0.0006),
        "currency_symbol": '￥',
    },
    "doubao-lite-128k":{
        "Pricing": (0.0008, 0.001),
        "currency_symbol": '￥',
    },
    "doubao-pro-32k":{
        "Pricing": (0.0008, 0.002),
        "currency_symbol": '￥',
    },
    "doubao-pro-128k":{
        "Pricing": (0.005, 0.009),
        "currency_symbol": '￥',
    },
}

def stream_chat_with_doubao(messages, model='doubao-lite-32k', endpoint_id=None, response_json=False, api_key=None, max_tokens=32000):
    import traceback
    import json
    import time
    
    # 详细日志记录API调用信息
    print(f"=== Doubao API Call Details ===")
    print(f"Model: {model}")
    print(f"Endpoint ID: {endpoint_id}")
    print(f"API Key: {'***' + api_key[-8:] if api_key and len(api_key) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    print(f"First Message: {json.dumps(messages[0] if messages else {}, ensure_ascii=False)[:200]}...")
    
    if api_key is None:
        error_msg = '未提供有效的 api_key！'
        print(f"❌ API Key Error: {error_msg}")
        raise Exception(error_msg)
    if endpoint_id is None:
        error_msg = '未提供有效的 endpoint_id！'
        print(f"❌ Endpoint ID Error: {error_msg}")
        raise Exception(error_msg)

    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    
    try:
        print(f"✅ Creating Doubao client...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        print(f"✅ Doubao client created successfully")
        
        request_params = {
            'model': endpoint_id,
            'messages': messages,
            'stream': True,
            'response_format': { "type": "json_object" } if response_json else None
        }
        
        print(f"\n🌐 === Doubao API Request Details ===")
        print(f"Base URL: {base_url}")
        print(f"Model (Endpoint ID): {endpoint_id}")
        print(f"Messages Count: {len(messages)}")
        print(f"Stream: True")
        print(f"Response Format: {'json_object' if response_json else 'text'}")
        safe_messages = [
            {**msg, 'content': msg['content'][:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')}
            for msg in messages
        ]
        print(f"Request Messages: {json.dumps(safe_messages, indent=2, ensure_ascii=False)}")
        print(f"=== End Doubao Request Details ===\n")
        
        print(f"🚀 Sending request to Doubao API")
        start_time = time.time()
        
        stream = client.chat.completions.create(**request_params)
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s, starting to stream response")
        
        messages.append({'role': 'assistant', 'content': ''})
        content = ''
        chunk_count = 0
        first_chunk_time = None
        
        for chunk in stream:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:  # Log first few chunks for debugging
                print(f"📦 Chunk #{chunk_count}: {str(chunk)[:200]}...")
            
            if chunk.choices:
                delta_content = chunk.choices[0].delta.content or ''
                content += delta_content
                
                # 对内容进行思考过程过滤（处理 <think> </think> 等标签）
                from prompts.prompt_utils import filter_thinking_process
                filtered_content = filter_thinking_process(content)
                
                messages[-1]['content'] = filtered_content
                yield messages
        
        total_time = time.time() - start_time
        print(f"✅ Doubao API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        return messages
        
    except Exception as e:
        print(f"❌ Doubao API Call Failed: {type(e).__name__}: {str(e)}")
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
        raise Exception(f"Doubao API调用失败 - {type(e).__name__}: {str(e)}")
        
    finally:
        print(f"=== Doubao API Call Finished ===\n")

if __name__ == '__main__':
    pass
