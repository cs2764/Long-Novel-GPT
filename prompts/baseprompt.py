import os
import re
from prompts.chat_utils import chat, log
from prompts.pf_parse_chat import parse_chat
from prompts.prompt_utils import load_text, match_code_block

def parser(response_msgs):
    content = response_msgs.response
    blocks = match_code_block(content)
    if blocks:
        concat_blocks = "\n".join(blocks)
        if concat_blocks.strip():
            content = concat_blocks
    return content


def clean_txt_content(content):
    """Remove comments and trim empty lines from txt content"""
    lines = []
    for line in content.split('\n'):
        if not line.startswith('//'):
            lines.append(line)
    return '\n'.join(lines).strip()


def load_prompt(dirname, name):
    # 确保路径使用正确的分隔符
    txt_path = os.path.normpath(os.path.join(dirname, f"{name}.txt"))
    
    # 检查文件是否存在
    if not os.path.exists(txt_path):
        print(f"Warning: Prompt file not found: {txt_path}")
        # 返回默认内容而不是崩溃
        return f"# {name}\n\n默认提示词内容，请检查文件路径：{txt_path}"
    
    text = load_text(txt_path)
    return text

def parse_prompt(text, **kwargs):
    """
        从text中解析PromptMessages。
        对于传入的key-values, key可以多也可以少。
        少的key和value为空的那轮对话会被删除。
        多的key不会管。
    """
    content = clean_txt_content(text)

    # Find all format keys in content using regex
    format_keys = set(re.findall(r'\{(\w+)\}', content))
    
    formatted_kwargs = {k: kwargs.get(k, '__delete__') or '__delete__' for k in format_keys}
    formatted_kwargs = {k: f"```\n{v.strip()}\n```" for k, v in formatted_kwargs.items()}
    prompt = content.format(**formatted_kwargs) if format_keys else content
    messages = parse_chat(prompt)
    for i in range(len(messages)-2, -1, -1):
        if '__delete__' in messages[i]['content']:
            assert messages[i]['role'] == 'user' and messages[i+1]['role'] == 'assistant', "__delete__ must be in user's message"
            messages.pop(i)
            messages.pop(i)
    
    return messages


def parse_input_keys(text):
    # Use regex to find the input keys line and parse keys
    match = re.search(r'//\s*输入：(.*?)(?:\n|$)', text)
    if not match:
        return []
        
    keys_str = match.group(1).strip()
        
    keys = [k.strip() for k in keys_str.split(',') if k.strip()]
    
    return keys

def main(model, dirname, user_prompt_text, **kwargs):
    # Load system prompt
    system_prompt = parse_prompt(load_prompt(dirname, "system_prompt"), **kwargs)
    
    load_from_file_flag = False
    if os.path.exists(os.path.join(dirname, user_prompt_text)):
        user_prompt_text = load_prompt(dirname, user_prompt_text)
        load_from_file_flag = True
    else:
        if not re.search(r'^user:\n', user_prompt_text, re.MULTILINE):
            user_prompt_text = f"user:\n{user_prompt_text}"
        
    user_prompt = parse_prompt(user_prompt_text, **kwargs)
    
    context_input_keys = parse_input_keys(user_prompt_text)
    if not context_input_keys:
        assert not load_from_file_flag, "从本地文件加载Prompt时，本地文件中注释必须指明输入！"
        context_kwargs = kwargs
    else:
        context_kwargs = {k: kwargs[k] for k in context_input_keys}
        assert all(context_kwargs.values()), "Missing required context keys"
    
    context_prompt = parse_prompt(load_prompt(dirname, "context_prompt"), **context_kwargs)
    
    # Combine all prompts
    final_prompt = system_prompt + context_prompt + user_prompt
    
    # Chat and parse results
    for response_msgs in chat(final_prompt, None, model, parse_chat=False):
        text = parser(response_msgs)
        ret = {'text': text, 'response_msgs': response_msgs}
        yield ret

    return ret



