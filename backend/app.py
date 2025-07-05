import json
import time

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.baseprompt import clean_txt_content, load_prompt

from core.writer_utils import KeyPointMsg
from core.draft_writer import DraftWriter
from core.plot_writer import PlotWriter
from core.outline_writer import OutlineWriter

from setting import setting_bp
from summary import process_novel
from backend_utils import get_model_config_from_provider_model
from config import MAX_NOVEL_SUMMARY_LENGTH, MAX_THREAD_NUM, ENABLE_ONLINE_DEMO

# 导入动态配置API
try:
    from dynamic_config_api import dynamic_config_bp
    app.register_blueprint(dynamic_config_bp)
    print("✅ 动态配置API已注册")
except ImportError as e:
    print(f"⚠️ 动态配置API导入失败: {e}")

app.register_blueprint(setting_bp)

# 添加配置
BACKEND_HOST = os.environ.get('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.environ.get('BACKEND_PORT', 7869))


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time())
    }), 200


def load_novel_writer(writer_mode, chunk_list, global_context, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num) -> DraftWriter:
    import traceback
    
    print(f"\n=== Loading Novel Writer ===")
    print(f"Writer Mode: {writer_mode}")
    print(f"Main Model: {main_model}")
    print(f"Sub Model: {sub_model}")
    
    try:
        print(f"🔧 Getting main model config...")
        main_model_config = get_model_config_from_provider_model(main_model)
        print(f"✅ Main model config obtained")
        
        print(f"🔧 Getting sub model config...")
        sub_model_config = get_model_config_from_provider_model(sub_model)
        print(f"✅ Sub model config obtained")
        
        kwargs = dict(
            xy_pairs=chunk_list,
            model=main_model_config,
            sub_model=sub_model_config,
        )

        kwargs['x_chunk_length'] = x_chunk_length
        kwargs['y_chunk_length'] = y_chunk_length
        kwargs['max_thread_num'] = max_thread_num
        
        print(f"🔧 Creating writer for mode: {writer_mode}")
        
        match writer_mode:
            case 'draft':
                kwargs['global_context'] = {}
                novel_writer = DraftWriter(**kwargs)
            case 'outline':
                kwargs['global_context'] = {'summary': global_context}
                novel_writer = OutlineWriter(**kwargs)
            case 'plot':
                kwargs['global_context'] = {'chapter': global_context}
                novel_writer = PlotWriter(**kwargs)
            case _:
                error_msg = f"unknown writer: {writer_mode}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
                
        print(f"✅ Novel writer created successfully")
        return novel_writer
        
    except Exception as e:
        print(f"❌ Error loading novel writer: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise
    finally:
        print(f"=== Novel Writer Loading Finished ===\n")





prompt_names = dict(
    outline = ['新建章节', '扩写章节', '润色章节'],
    plot = ['新建剧情', '扩写剧情', '润色剧情'],
    draft = ['新建正文', '扩写正文', '润色正文'],
)

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

prompt_dirname = dict(
    outline = os.path.join(project_root, 'prompts', '创作章节'),
    plot = os.path.join(project_root, 'prompts', '创作剧情'),
    draft = os.path.join(project_root, 'prompts', '创作正文'),
)


PROMPTS = {}
for type_name, dirname in prompt_dirname.items():
    PROMPTS[type_name] = {'prompt_names': prompt_names[type_name]}
    for name in prompt_names[type_name]:
        try:
            content = clean_txt_content(load_prompt(dirname, name))
            if content.startswith("user:\n"):
                content = content[len("user:\n"):]
            PROMPTS[type_name][name] = {'content': content}
        except Exception as e:
            print(f"⚠️ 加载提示词文件失败: {dirname}/{name}.txt - {e}")
            # 使用默认内容继续运行而不是崩溃
            PROMPTS[type_name][name] = {'content': f"# {name}\n\n提示词文件加载失败: {e}"}


@app.route('/prompts', methods=['GET'])
def get_prompts():
    return jsonify(PROMPTS)

def get_delta_chunks(prev_chunks, curr_chunks):
    """Calculate delta between previous and current chunks"""
    if not prev_chunks or len(prev_chunks) != len(curr_chunks):
        return "init", curr_chunks
    
    # Check if all strings in current chunks start with their corresponding previous strings
    is_delta = True
    for prev_chunk, curr_chunk in zip(prev_chunks, curr_chunks):
        if len(prev_chunk) != len(curr_chunk):
            is_delta = False
            break
        for prev_str, curr_str in zip(prev_chunk, curr_chunk):
            if not curr_str.startswith(prev_str):
                is_delta = False
                break
        if not is_delta:
            break
    
    if not is_delta:
        return "init", curr_chunks
    
    # Calculate deltas
    delta_chunks = []
    for prev_chunk, curr_chunk in zip(prev_chunks, curr_chunks):
        delta_chunk = []
        for prev_str, curr_str in zip(prev_chunk, curr_chunk):
            delta_str = curr_str[len(prev_str):]
            delta_chunk.append(delta_str)
        delta_chunks.append(delta_chunk)
    
    return "delta", delta_chunks


def call_write(writer_mode, chunk_list, global_context, chunk_span, prompt_content, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num, only_prompt):
    import traceback
    
    print(f"\n=== Novel Writing Process Started ===")
    print(f"Writer Mode: {writer_mode}")
    print(f"Main Model: {main_model}")
    print(f"Sub Model: {sub_model}")
    print(f"Max Thread Num: {max_thread_num}")
    print(f"Chunk List Length: {len(chunk_list) if chunk_list else 0}")
    print(f"Global Context: {str(global_context)[:200]}...")
    
    try:
        if ENABLE_ONLINE_DEMO:
            if max_thread_num > MAX_THREAD_NUM:
                error_msg = "在线Demo模型下，最大线程数不能超过" + str(MAX_THREAD_NUM) + "！"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
        
        # 输入的chunk_list中每个chunk需要加上换行，除了最后一个chunk（因为是从页面中各个chunk传来的）
        chunk_list = [[e.strip() + ('\n' if e.strip() and rowi != len(chunk_list)-1 else '') for e in row] for rowi, row in enumerate(chunk_list)]
        print(f"✅ Chunk list processed")

        prev_chunks = None
        def delta_wrapper(chunk_list, done=False, msg=None):
            # 返回的chunk_list中每个chunk需要去掉换行
            chunk_list = [[e.strip() for e in row] for row in chunk_list]

            nonlocal prev_chunks
            if prev_chunks is None:
                prev_chunks = chunk_list
                return {
                    "done": done,
                    "chunk_type": "init",
                    "chunk_list": chunk_list,
                    "msg": msg
                }
            else:
                chunk_type, new_chunks = get_delta_chunks(prev_chunks, chunk_list)
                prev_chunks = chunk_list
                return {
                    "done": done,
                    "chunk_type": chunk_type,
                    "chunk_list": new_chunks,
                    "msg": msg
                }
            
        print(f"🔧 Loading novel writer...")
        novel_writer = load_novel_writer(writer_mode, chunk_list, global_context, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num)
        print(f"✅ Novel writer loaded successfully")
        
    except Exception as e:
        print(f"❌ Error in call_write setup: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise
    

    # draft需要映射，所以进行初始划分
    if writer_mode == 'draft':
        target_chunk = novel_writer.get_chunk(pair_span=chunk_span)
        new_target_chunk = novel_writer.map_text_wo_llm(target_chunk)
        novel_writer.apply_chunks([target_chunk], [new_target_chunk])
        chunk_span = novel_writer.get_chunk_pair_span(new_target_chunk)
    
    init_novel_writer = load_novel_writer(writer_mode, list(novel_writer.xy_pairs), global_context, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num)
    
    # TODO: writer.write 应该保证无论什么prompt，都能够同时适应y为空和y有值地情况
    # 换句话说，就是虽然可以单列出一个"新建正文"，但用扩写正文也能实现同样的效果。
    generator = novel_writer.write(prompt_content, pair_span=chunk_span) 
    
    prompt_outputs = []
    last_yield_time = time.time()  # Initialize the last yield time

    prompt_name = ''
    for kp_msg in generator:
        if isinstance(kp_msg, KeyPointMsg):
            # 如果要支持关键节点保存，需要计算一个编辑上的更改，然后在这里yield writer
            prompt_name = kp_msg.prompt_name
            continue
        else:
            chunk_list = kp_msg

        current_cost = 0
        currency_symbol = ''
        current_model = ''
        data_chunks = []
        prompt_outputs.clear()
        for e in chunk_list:
            if e is None: continue  # e为None说明该chunk还未处理
            output, chunk = e
            if output is None: continue # output为None说明该chunk未yield就return，说明未调用llm
            prompt_outputs.append(output)
            current_text = ""
            current_model = output['response_msgs'].model
            current_cost += output['response_msgs'].cost
            currency_symbol = output['response_msgs'].currency_symbol
            if 'plot2text' in output:
                current_text += f"正在建立映射关系..." + '\n'
            else:
                current_text = output['text']
            data_chunks.append((chunk.x_chunk, chunk.y_chunk, current_text))
            
        if only_prompt:
            yield {'prompts': [e['response_msgs'] for e in prompt_outputs]}
            return

        current_time = time.time()
        if current_time - last_yield_time >= 0.2:  # Check if 0.2 seconds have passed
            yield delta_wrapper(data_chunks, done=False, msg=f"正在 {prompt_name} （{len(prompt_outputs)} / {len(chunk_list)}）" + f" 模型：{current_model} 花费：{current_cost:.5f}{currency_symbol}" if current_model else '')
            last_yield_time = current_time  # Update the last yield time

    # 这里是计算出一个编辑上的更改，方便前端显示，后续diff功能将不由writer提供，因为这是为了显示的要求
    data_chunks = init_novel_writer.diff_to(novel_writer, pair_span=chunk_span)

    yield delta_wrapper(data_chunks, done=True, msg='创作完成!')


@app.route('/write', methods=['POST'])
def write():
    data = request.json                 
    writer_mode = data['writer_mode']
    chunk_list = data['chunk_list']
    chunk_span = data['chunk_span']
    prompt_content = data['prompt_content']
    x_chunk_length = data['x_chunk_length']
    y_chunk_length = data['y_chunk_length']
    main_model = data['main_model']
    sub_model = data['sub_model']
    global_context = data['global_context']
    only_prompt = data['only_prompt']
    
    # Update settings if provided
    if 'settings' in data:
        max_thread_num = data['settings']['MAX_THREAD_NUM']

    # Generate unique stream ID
    stream_id = str(time.time())
    active_streams[stream_id] = True
    
    def generate():
        try:
            # Send stream ID to client
            yield f"data: {json.dumps({'stream_id': stream_id})}\n\n"

            for result in call_write(writer_mode, list(chunk_list), global_context, chunk_span, prompt_content, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num, only_prompt):
                if not active_streams.get(stream_id, False):
                    # Stream was stopped by client
                    print(f"Stream was stopped by client: {stream_id}")
                    return
                    
                yield f"data: {json.dumps(result)}\n\n"
        except Exception as e:
            error_msg = f"创作出错：\n{str(e)}"
            error_chunk_list = [[*e[:2], error_msg] for e in chunk_list[chunk_span[0]:chunk_span[1]]]
            
            error_data = {
                "done": True,
                "chunk_type": "init",
                "chunk_list": error_chunk_list
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        finally:
            # Clean up stream tracking
            if stream_id in active_streams:
                del active_streams[stream_id]

    return Response(generate(), mimetype='text/event-stream')


@app.route('/summary', methods=['POST'])
def process_novel_text():
    data = request.json
    content = data['content']
    novel_name = data['novel_name']

    # Generate unique stream ID
    stream_id = str(time.time())
    active_streams[stream_id] = True

    def generate():
        try:
            yield f"data: {json.dumps({'stream_id': stream_id})}\n\n"

            main_model = get_model_config_from_provider_model(data['main_model'])
            sub_model = get_model_config_from_provider_model(data['sub_model'])
            max_novel_summary_length = data['settings']['MAX_NOVEL_SUMMARY_LENGTH']
            max_thread_num = data['settings']['MAX_THREAD_NUM']
            last_yield_time = 0
            for result in process_novel(content, novel_name, main_model, sub_model, max_novel_summary_length, max_thread_num):
                if not active_streams.get(stream_id, False):
                    # Stream was stopped by client
                    print(f"Stream was stopped by client: {stream_id}")
                    return
                    
                current_time = time.time()
                yield_value = f"data: {json.dumps(result)}\n\n"
                if current_time - last_yield_time >= 0.2:
                    last_yield_time = current_time
                    yield yield_value
            if current_time - last_yield_time < 0.2:
                # Save last yield to yaml file
                import yaml
                result_dict = json.loads(yield_value.replace('data: ', '').strip())
                with open('tmp.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(result_dict, f, allow_unicode=True)
                    
                yield yield_value   # Ensure last yield is returned
            
        except Exception as e:
            error_data = {
                "progress_msg": f"处理出错：{str(e)}",
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        finally:
            # Clean up stream tracking
            if stream_id in active_streams:
                del active_streams[stream_id]

    return Response(generate(), mimetype='text/event-stream')

# Dictionary to track active streams
active_streams = {}

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    data = request.json
    stream_id = data.get('stream_id')
    if stream_id in active_streams:
        active_streams[stream_id] = False
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=False) 