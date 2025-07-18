import qianfan
from .chat_messages import ChatMessages

# ak和sk获取：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application

# 价格：https://cloud.baidu.com/doc/WENXINWORKSHOP/s/hlrk4akp7

wenxin_model_config = {
    "ERNIE-3.5-8K":{
        "Pricing": (0.0008, 0.002),
        "currency_symbol": '￥',
    },
    "ERNIE-4.0-8K":{
        "Pricing": (0.03, 0.09),
        "currency_symbol": '￥',
    },
    "ERNIE-Novel-8K":{
        "Pricing": (0.04, 0.12),
        "currency_symbol": '￥',
    }
}


def stream_chat_with_wenxin(messages, model='ERNIE-Bot', response_json=False, ak=None, sk=None, max_tokens=6000):
    import traceback
    import json
    import time
    
    # 详细日志记录API调用信息
    print(f"=== Wenxin (Baidu) API Call Details ===")
    print(f"Model: {model}")
    print(f"AK: {'***' + ak[-8:] if ak and len(ak) > 8 else 'None'}")
    print(f"SK: {'***' + sk[-8:] if sk and len(sk) > 8 else 'None'}")
    print(f"Max Tokens: {max_tokens}")
    print(f"Response JSON: {response_json}")
    print(f"Messages Count: {len(messages)}")
    print(f"First Message: {json.dumps(messages[0] if messages else {}, ensure_ascii=False)[:200]}...")
    
    if ak is None or sk is None:
        error_msg = '未提供有效的 ak 和 sk！'
        print(f"❌ API Key Error: {error_msg}")
        raise Exception(error_msg)

    try:
        print(f"✅ Creating Wenxin client...")
        client = qianfan.ChatCompletion(ak=ak, sk=sk)
        print(f"✅ Wenxin client created successfully")
        
        # 构建请求参数
        system_msg = messages[0]['content'] if messages[0]['role'] == 'system' else None
        chat_messages = messages if messages[0]['role'] != 'system' else messages[1:]
        
        request_params = {
            'model': model,
            'system': system_msg,
            'messages': chat_messages,
            'stream': True,
            'response_format': 'json_object' if response_json else 'text'
        }
        
        print(f"\n🌐 === Wenxin API Request Details ===")
        print(f"Model: {model}")
        print(f"System Message: {system_msg[:100] + '...' if system_msg and len(system_msg) > 100 else system_msg}")
        print(f"Chat Messages Count: {len(chat_messages)}")
        print(f"Stream: True")
        print(f"Response Format: {'json_object' if response_json else 'text'}")
        print(f"=== End Wenxin Request Details ===\n")
        
        print(f"🚀 Sending request to Wenxin API")
        start_time = time.time()
        
        chatstream = client.do(**request_params)
        
        print(f"✅ API request initiated successfully in {time.time() - start_time:.2f}s, starting to stream response")
        
        messages.append({'role': 'assistant', 'content': ''})
        content = ''
        chunk_count = 0
        first_chunk_time = None
        
        for part in chatstream:
            chunk_count += 1
            if first_chunk_time is None:
                first_chunk_time = time.time()
                print(f"📦 First chunk received in {first_chunk_time - start_time:.2f}s")
            
            if chunk_count <= 3:  # Log first few chunks for debugging
                print(f"📦 Chunk #{chunk_count}: {str(part)[:200]}...")
            
            content += part['body']['result'] or ''
            
            # 对内容进行思考过程过滤（处理 <think> </think> 等标签）
            from prompts.prompt_utils import filter_thinking_process
            filtered_content = filter_thinking_process(content)
            
            messages[-1]['content'] = filtered_content
            yield messages
        
        total_time = time.time() - start_time
        print(f"✅ Wenxin API call completed successfully in {total_time:.2f}s, received {chunk_count} chunks")
        return messages
        
    except Exception as e:
        print(f"❌ Wenxin API Call Failed: {type(e).__name__}: {str(e)}")
        print(f"📍 Full traceback:")
        traceback.print_exc()
        
        # 重新抛出异常，但包含更多信息
        raise Exception(f"Wenxin API调用失败 - {type(e).__name__}: {str(e)}")
        
    finally:
        print(f"=== Wenxin API Call Finished ===\n")

    
if __name__ == '__main__':
    pass