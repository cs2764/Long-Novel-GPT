import difflib
import json
import yaml
import chardet
from jinja2 import Environment, FileSystemLoader  

import re
import sys, os
root_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../.."))
if root_path not in sys.path:
    sys.path.append(root_path)

from llm_api.chat_messages import ChatMessages

def can_parse_json(response):
    try:
        json.loads(response)
        return True
    except:
        return False

def filter_thinking_process(text):
    """过滤掉思考过程，支持多种格式的思考标签"""
    if not text:
        return text
    
    # 过滤 <think> </think> 标签
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 过滤 <thinking> </thinking> 标签
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 过滤 <thought> </thought> 标签
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 过滤 <reasoning> </reasoning> 标签
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 清理多余的空白行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def match_first_json_block(response):
    # 首先过滤掉思考过程
    filtered_response = filter_thinking_process(response)
    
    if can_parse_json(filtered_response):
        return filtered_response
    
    pattern = r"(?<=[\r\n])```json(.*?)```(?=[\r\n])"
    matches = re.findall(pattern, '\n' + filtered_response + '\n', re.DOTALL)
    if not matches:
        pattern = r"(?<=[\r\n])```(.*?)```(?=[\r\n])"
        matches = re.findall(pattern, '\n' + filtered_response + '\n', re.DOTALL)
        
    if matches:
        json_block = matches[0]
        # 对JSON块也进行思考过程过滤
        json_block = filter_thinking_process(json_block)
        if can_parse_json(json_block):
            return json_block
        else:
            json_block = json_block.replace('\r\n', '')  # 在continue generate情况下，不同部分之间可能有多出的换行符，导致合起来之后json解析失败
            if can_parse_json(json_block):
                return json_block
            else:
                raise Exception(f"无法解析JSON代码块")
    else:
        raise Exception(f"没有匹配到JSON代码块")
    
def parse_first_json_block(response_msgs: ChatMessages):
    assert response_msgs[-1]['role'] == 'assistant'
    return json.loads(match_first_json_block(response_msgs[-1]['content']))

def match_code_block(response):
    response = re.sub(r'\r\n', r'\n', response)
    response = re.sub(r'\r', r'\n', response)
    pattern = r"```(?:\S*\s)(.*?)```"
    matches = re.findall(pattern, response + '```', re.DOTALL)
    return matches

def json_dumps(json_object):
    return json.dumps(json_object, ensure_ascii=False, indent=1)

def parse_chunks_by_separators(string, separators):
    separator_pattern = r"^\s*###\s*(" + "|".join(separators) + r")\s*\n"

    chunks = re.split(separator_pattern, string, flags=re.MULTILINE)

    ret = {}

    current_title = None
    
    for i, chunk in enumerate(chunks):
        if i % 2 == 1: 
            current_title = chunk.strip()
            ret[current_title] = ""
        elif current_title:
            ret[current_title] += chunk.strip()

    return ret

def construct_chunks_and_separators(chunk2separator):
    return "\n\n".join([f"### {k}\n{v}" for k, v in chunk2separator.items()])

def match_chunk_span_in_text(chunk, text):
    diff = difflib.Differ().compare(chunk, text)

    chunk_i = 0
    text_i = 0

    for tag in diff:
        if tag.startswith(' '):
            chunk_i += 1
            text_i += 1
        elif tag.startswith('+'):
            text_i += 1
        else:
            chunk_i += 1
        
        if chunk_i == 1:
            l = text_i - 1
        
        if chunk_i == len(chunk):
            r = text_i
            return l, r

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:  
        return yaml.safe_load(file)  

def load_text(file_path, read_size=None): 
    # 规范化文件路径
    file_path = os.path.normpath(file_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the raw bytes first
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read(read_size)
    except Exception as e:
        raise IOError(f"Failed to read file {file_path}: {str(e)}")
    
    # Detect the encoding
    result = chardet.detect(raw_data[:10000])
    encoding = result['encoding'] or 'utf-8'  # Fallback to utf-8 if detection fails
    
    # Decode the content with detected encoding
    try:
        return raw_data.decode(encoding, errors='ignore')
    except UnicodeDecodeError:
        # Fallback to utf-8 if the detected encoding fails
        return raw_data.decode('utf-8', errors='ignore')

def load_jinja2_template(file_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(file_path)))
    template = env.get_template(os.path.basename(file_path)) 

    return template 


