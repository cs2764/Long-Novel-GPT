import json
import os
from prompts.chat_utils import chat
from prompts.prompt_utils import load_jinja2_template, match_first_json_block


def parser(response_msgs, text_chunks, topk):
    content = response_msgs[-1]['content']

    try:
        content = match_first_json_block(content)
        content_json = json.loads(content)
        if content_json and isinstance(topk_indexes := next(iter(content_json.values())), list):
                # 过滤掉思考过程，只保留数字索引
                numeric_indexes = []
                for e in topk_indexes[:topk]:
                    try:
                        # 尝试转换为整数，如果失败则跳过
                        idx = int(e) - 1
                        if 0 <= idx < len(text_chunks):
                            numeric_indexes.append(idx)
                    except (ValueError, TypeError):
                        # 跳过无法转换为整数的元素（如思考过程中的文本）
                        continue
                
                if numeric_indexes:
                    return numeric_indexes[:topk]
    except Exception as e:
        import traceback
        traceback.print_exc()
    
    return None


def main(model, question, text_chunks, topk):
    template = load_jinja2_template(os.path.join(os.path.dirname(os.path.join(__file__)), "prompt.jinja2"))

    prompt = template.render(references=text_chunks, 
                             question=question,
                             topk=topk)
    
    for response_msgs in chat([], prompt, model, max_tokens=10 + topk * 4, response_json=True, parse_chat=True):
        try: 
            match_first_json_block(response_msgs[-1]['content'])
        except Exception: 
            pass
        else:
            topk_indexes = parser(response_msgs, text_chunks, topk)
            return {'topk_indexes': topk_indexes, 'response_msgs':response_msgs}

        yield response_msgs
    


