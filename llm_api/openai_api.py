import httpx
from openai import OpenAI
from .chat_messages import ChatMessages

# Pricing reference: https://openai.com/api/pricing/
gpt_model_config = {
    "gpt-4o": {
        "Pricing": (2.50/1000, 10.00/1000),
        "currency_symbol": '$',
    },
    "gpt-4o-mini": {
        "Pricing": (0.15/1000, 0.60/1000),
        "currency_symbol": '$',
    },
    "o1-preview": {
        "Pricing": (15/1000, 60/1000),
        "currency_symbol": '$',
    },
    "o1-mini": {
        "Pricing": (3/1000, 12/1000),
        "currency_symbol": '$',
    },
}
# https://platform.openai.com/docs/guides/reasoning

def stream_chat_with_gpt(messages, model='gpt-3.5-turbo-1106', response_json=False, api_key=None, base_url=None, max_tokens=4_096, n=1, proxies=None):
    import traceback
    import json
    import requests
    import time
    
    # 详细日志记录API调用信息
    print(f"=== OpenAI API Call Details ===")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {'***' + api_key[-8:] if api_key and len(api_key) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    print(f"First Message: {json.dumps(messages[0] if messages else {}, ensure_ascii=False)[:200]}...")
    print(f"Proxies: {proxies}")
    
    if api_key is None:
        error_msg = '未提供有效的 api_key！'
        print(f"❌ API Key Error: {error_msg}")
        raise Exception(error_msg)
    
    # 构建实际的HTTP请求详细信息
    api_url = f"{base_url or 'https://api.openai.com/v1'}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if base_url and "openrouter.ai" in base_url:
        headers.update({
            "HTTP-Referer": "https://github.com/Long-Novel-GPT",
            "X-Title": "Long-Novel-GPT"
        })
    
    request_body = {
        'stream': True,
        'model': model, 
        'messages': messages, 
        'max_tokens': max_tokens,
        'n': n
    }
    
    if response_json:
        request_body['response_format'] = {"type": "json_object"}
        
    # 显示实际发送的HTTP请求详细信息
    print(f"\n🌐 === HTTP Request Details ===")
    print(f"URL: {api_url}")
    print(f"Method: POST")
    print(f"Headers:")
    for key, value in headers.items():
        if key.lower() == 'authorization':
            print(f"  {key}: Bearer ***{value.split()[-1][-8:] if len(value.split()) > 1 else '***'}")
        else:
            print(f"  {key}: {value}")
    
    print(f"Request Body:")
    # 为了显示，创建一个安全的请求体副本
    safe_body = request_body.copy()
    safe_body['messages'] = [
        {**msg, 'content': msg['content'][:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')}
        for msg in messages
    ]
    print(json.dumps(safe_body, indent=2, ensure_ascii=False))
    print(f"=== End HTTP Request Details ===\n")
    
    client_params = {
        "api_key": api_key,
    }

    if base_url:
        client_params['base_url'] = base_url
        print(f"✅ Using custom base URL: {base_url}")

    if proxies:
        httpx_client = httpx.Client(proxy=proxies)
        client_params["http_client"] = httpx_client
        print(f"✅ Using proxy: {proxies}")
    
    try:
        client = OpenAI(**client_params)
        print("✅ OpenAI client created successfully")

        if model in ['o1-preview', ] and messages[0]['role'] == 'system':
            print("🔄 Converting system message for o1-preview model")
            messages[0:1] = [{'role': 'user', 'content': messages[0]['content']}, {'role': 'assistant', 'content': ''}]
        
        request_params = {
            'stream': True,
            'model': model, 
            'messages': messages, 
            'max_tokens': max_tokens,
            'response_format': { "type": "json_object" } if response_json else None,
            'n': n
        }
        
        print(f"🚀 Sending request to {api_url}")
        start_time = time.time()
        
        chatstream = client.chat.completions.create(**request_params)
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s, starting to stream response")
        
        messages.append({'role': 'assistant', 'content': ''})
        content = ['' for _ in range(n)]
        chunk_count = 0
        first_chunk_time = None
        
        for part in chatstream:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:  # Log first few chunks for debugging
                print(f"📦 Chunk #{chunk_count}: {str(part)[:200]}...")
            
            for choice in part.choices:
                content[choice.index] += choice.delta.content or ''
                messages[-1]['content'] = content if n > 1 else content[0]
                yield messages
        
        total_time = time.time() - start_time
        print(f"✅ API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        return messages
        
    except Exception as e:
        print(f"❌ API Call Failed: {type(e).__name__}: {str(e)}")
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
        raise Exception(f"OpenAI API调用失败 - {type(e).__name__}: {str(e)}")
        
    finally:
        print(f"=== API Call Finished ===\n")

    
if __name__ == '__main__':
    pass
