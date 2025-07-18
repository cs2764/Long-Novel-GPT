import json
import os
import traceback
import time

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import sys
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

# Enhanced prompt directories
enhanced_prompt_dirname = dict(
    outline = os.path.join(project_root, 'prompts', 'enhanced', '创作章节'),
    plot = os.path.join(project_root, 'prompts', 'enhanced', '创作剧情'),
    draft = os.path.join(project_root, 'prompts', 'enhanced', '创作正文'),
)


PROMPTS = {}
# Load regular prompts
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

# Load enhanced prompts
PROMPTS['enhanced'] = {}
for type_name, dirname in enhanced_prompt_dirname.items():
    PROMPTS['enhanced'][type_name] = {'prompt_names': prompt_names[type_name]}
    for name in prompt_names[type_name]:
        try:
            content = clean_txt_content(load_prompt(dirname, name))
            if content.startswith("user:\n"):
                content = content[len("user:\n"):]
            PROMPTS['enhanced'][type_name][name] = {'content': content}
        except Exception as e:
            print(f"⚠️ 加载增强提示词文件失败: {dirname}/{name}.txt - {e}")
            # Fallback to regular prompt if enhanced version fails
            if type_name in PROMPTS and name in PROMPTS[type_name]:
                PROMPTS['enhanced'][type_name][name] = PROMPTS[type_name][name]
            else:
                PROMPTS['enhanced'][type_name][name] = {'content': f"# {name}\n\n增强提示词文件加载失败: {e}"}


@app.route('/prompts', methods=['GET'])
def get_prompts():
    return jsonify(PROMPTS)

@app.route('/generate_enhanced_prompts', methods=['POST'])
def generate_enhanced_prompts():
    """Generate enhanced prompts - since they're already created, just return success"""
    try:
        # Check if enhanced prompts directory exists and has content
        enhanced_exists = all(
            os.path.exists(dirname) and 
            any(os.path.exists(os.path.join(dirname, f"{name}.txt")) for name in prompt_names[type_name])
            for type_name, dirname in enhanced_prompt_dirname.items()
        )
        
        if enhanced_exists:
            return jsonify({'success': True, 'message': '增强提示词已可用'})
        else:
            return jsonify({'success': False, 'error': '增强提示词文件未找到'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
    
    print(f"\n{'='*60}")
    print(f"🚀 Novel Writing Process Started")
    print(f"{'='*60}")
    print(f"📝 Writer Mode: {writer_mode}")
    print(f"🤖 Main Model: {main_model}")
    print(f"🤖 Sub Model: {sub_model}")
    print(f"🔢 Max Thread Num: {max_thread_num}")
    print(f"📋 Chunk List Length: {len(chunk_list) if chunk_list else 0}")
    print(f"📄 Global Context Length: {len(str(global_context)) if global_context else 0} characters")
    print(f"📄 Global Context Preview: {str(global_context)[:200]}...")
    print(f"⚙️ Chunk Span: {chunk_span}")
    print(f"📏 X Chunk Length: {x_chunk_length}")
    print(f"📏 Y Chunk Length: {y_chunk_length}")
    print(f"🎯 Only Prompt: {only_prompt}")
    print(f"💼 Prompt Content Length: {len(prompt_content) if prompt_content else 0} characters")
    
    # 检查是否使用LM Studio本地模型
    if main_model and ('localhost' in main_model or '127.0.0.1' in main_model):
        print(f"🏠 检测到LM Studio本地模型，将使用延长的超时时间")
        
    start_time = time.time()
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"{'='*60}")
    print(f"✅ 初始化完成")
    print(f"{'='*60}\n")
    
    # 统计信息
    total_processed_chunks = 0
    total_api_calls = 0
    total_cost = 0.0
    total_chars_generated = 0
    
    try:
        if ENABLE_ONLINE_DEMO:
            if max_thread_num > MAX_THREAD_NUM:
                error_msg = "在线Demo模型下，最大线程数不能超过" + str(MAX_THREAD_NUM) + "！"
                print(f"❌ 参数验证失败: {error_msg}")
                raise Exception(error_msg)
        
        print(f"🔄 正在处理chunk列表...")
        # 输入的chunk_list中每个chunk需要加上换行，除了最后一个chunk（因为是从页面中各个chunk传来的）
        original_chunk_count = len(chunk_list)
        chunk_list = [[e.strip() + ('\n' if e.strip() and rowi != len(chunk_list)-1 else '') for e in row] for rowi, row in enumerate(chunk_list)]
        print(f"✅ Chunk列表预处理完成，共处理 {original_chunk_count} 个chunk")

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
            
        print(f"🔧 正在加载小说写作器...")
        writer_load_start = time.time()
        novel_writer = load_novel_writer(writer_mode, chunk_list, global_context, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num)
        writer_load_time = time.time() - writer_load_start
        print(f"✅ 小说写作器加载完成，耗时: {writer_load_time:.2f}秒")
        
    except Exception as e:
        print(f"❌ call_write 初始化失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        print(f"   完整堆栈跟踪:")
        traceback.print_exc()
        raise
    
    # draft需要映射，所以进行初始划分
    if writer_mode == 'draft':
        print(f"📝 处理draft模式的特殊逻辑...")
        target_chunk = novel_writer.get_chunk(pair_span=chunk_span)
        new_target_chunk = novel_writer.map_text_wo_llm(target_chunk)
        novel_writer.apply_chunks([target_chunk], [new_target_chunk])
        chunk_span = novel_writer.get_chunk_pair_span(new_target_chunk)
        print(f"✅ Draft模式初始化完成，更新后的chunk_span: {chunk_span}")
    
    init_novel_writer = load_novel_writer(writer_mode, list(novel_writer.xy_pairs), global_context, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num)
    
    # TODO: writer.write 应该保证无论什么prompt，都能够同时适应y为空和y有值地情况
    # 换句话说，就是虽然可以单列出一个"新建正文"，但用扩写正文也能实现同样的效果。
    print(f"🎯 开始执行写作生成器...")
    generator = novel_writer.write(prompt_content, pair_span=chunk_span) 
    
    prompt_outputs = []
    last_yield_time = time.time()  # Initialize the last yield time
    last_progress_info = None  # Track last progress to avoid duplicates
    step_count = 0

    prompt_name = ''
    for kp_msg in generator:
        if isinstance(kp_msg, KeyPointMsg):
            # 如果要支持关键节点保存，需要计算一个编辑上的更改，然后在这里yield writer
            prompt_name = kp_msg.prompt_name
            step_count += 1
            print(f"🔄 步骤 {step_count}: 开始执行 {prompt_name}")
            continue
        else:
            chunk_list = kp_msg

        current_cost = 0
        currency_symbol = ''
        current_model = ''
        data_chunks = []
        prompt_outputs.clear()
        
        # 处理API调用结果
        processed_chunks = 0
        api_call_count = 0
        
        for e in chunk_list:
            if e is None: continue  # e为None说明该chunk还未处理
            output, chunk = e
            if output is None: continue # output为None说明该chunk未yield就return，说明未调用llm
            
            processed_chunks += 1
            api_call_count += 1
            total_api_calls += 1
            
            prompt_outputs.append(output)
            current_text = ""
            current_model = output['response_msgs'].model
            chunk_cost = output['response_msgs'].cost
            current_cost += chunk_cost
            total_cost += chunk_cost
            currency_symbol = output['response_msgs'].currency_symbol
            
            # 计算生成的字符数
            text_length = len(output.get('text', ''))
            total_chars_generated += text_length
            
            if 'plot2text' in output:
                current_text += f"正在建立映射关系..." + '\n'
            else:
                current_text = output['text']
            data_chunks.append((chunk.x_chunk, chunk.y_chunk, current_text))
            
        total_processed_chunks += processed_chunks
        
        if only_prompt:
            print(f"✅ 仅查看Prompt模式，返回 {len(prompt_outputs)} 个Prompt")
            yield {'prompts': [e['response_msgs'] for e in prompt_outputs]}
            return

        current_time = time.time()
        step_elapsed = current_time - last_yield_time
        
        # Create progress info tuple to check for duplicates
        progress_info = (prompt_name, len(prompt_outputs), len(chunk_list), current_model, current_cost)
        
        if current_time - last_yield_time >= 0.2 and progress_info != last_progress_info:  # Check time and avoid duplicates
            progress_msg = f"正在 {prompt_name} （{len(prompt_outputs)} / {len(chunk_list)}）"
            if current_model:
                progress_msg += f" 模型：{current_model} 花费：{current_cost:.5f}{currency_symbol}"
            
            # 更详细的控制台日志
            print(f"📊 {'='*50}")
            print(f"📊 创作进度更新 - 步骤 {step_count}")
            print(f"📊 {'='*50}")
            print(f"📝 当前步骤: {prompt_name}")
            print(f"🔢 处理进度: {len(prompt_outputs)} / {len(chunk_list)} 个块")
            print(f"🤖 使用模型: {current_model}")
            print(f"💰 当前花费: {current_cost:.5f}{currency_symbol}")
            print(f"⏱️ 步骤用时: {step_elapsed:.2f}秒")
            print(f"🧱 数据块数量: {len(data_chunks)}")
            print(f"📊 API调用次数: {api_call_count}")
            print(f"📄 生成字符数: {sum(len(chunk[2]) for chunk in data_chunks)}")
            print(f"{'='*50}")
            
            # 累计统计信息
            print(f"📈 累计统计信息:")
            print(f"   📊 总处理块数: {total_processed_chunks}")
            print(f"   🔄 总API调用数: {total_api_calls}")
            print(f"   💰 总花费: {total_cost:.5f}{currency_symbol}")
            print(f"   📄 总生成字符数: {total_chars_generated}")
            print(f"   ⏱️ 总用时: {current_time - start_time:.2f}秒")
            print(f"{'='*50}\n")
            
            yield delta_wrapper(data_chunks, done=False, msg=progress_msg)
            last_yield_time = current_time  # Update the last yield time
            last_progress_info = progress_info  # Update the last progress info

    # 最终处理
    print(f"🔄 正在计算最终差异...")
    diff_start = time.time()
    # 这里是计算出一个编辑上的更改，方便前端显示，后续diff功能将不由writer提供，因为这是为了显示的要求
    data_chunks = init_novel_writer.diff_to(novel_writer, pair_span=chunk_span)
    diff_time = time.time() - diff_start
    print(f"✅ 差异计算完成，耗时: {diff_time:.2f}秒")
    
    # 最终统计信息
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🎉 小说创作过程完成！")
    print(f"{'='*60}")
    print(f"📊 最终统计信息:")
    print(f"   📝 写作模式: {writer_mode}")
    print(f"   🔢 处理步骤数: {step_count}")
    print(f"   📊 总处理块数: {total_processed_chunks}")
    print(f"   🔄 总API调用数: {total_api_calls}")
    print(f"   💰 总花费: {total_cost:.5f}{currency_symbol}")
    print(f"   📄 总生成字符数: {total_chars_generated}")
    print(f"   ⏱️ 总用时: {total_time:.2f}秒")
    print(f"   📈 平均每API调用用时: {total_time/total_api_calls:.2f}秒" if total_api_calls > 0 else "")
    print(f"   📈 平均每字符成本: {total_cost/total_chars_generated:.8f}{currency_symbol}" if total_chars_generated > 0 else "")
    print(f"   📈 生成效率: {total_chars_generated/total_time:.2f} 字符/秒" if total_time > 0 else "")
    print(f"{'='*60}")
    
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
    
    # 记录请求信息
    print(f"\n{'='*60}")
    print(f"🌐 收到/write请求")
    print(f"{'='*60}")
    print(f"📝 Writer Mode: {writer_mode}")
    print(f"🆔 Stream ID: {stream_id}")
    print(f"📋 Chunk List Length: {len(chunk_list) if chunk_list else 0}")
    print(f"⚙️ Chunk Span: {chunk_span}")
    print(f"🤖 Main Model: {main_model}")
    print(f"🤖 Sub Model: {sub_model}")
    print(f"🎯 Only Prompt: {only_prompt}")
    print(f"⏰ 请求时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"{'='*60}\n")
    
    def generate():
        request_start_time = time.time()
        try:
            # Send stream ID to client
            yield f"data: {json.dumps({'stream_id': stream_id})}\n\n"

            result_count = 0
            for result in call_write(writer_mode, list(chunk_list), global_context, chunk_span, prompt_content, x_chunk_length, y_chunk_length, main_model, sub_model, max_thread_num, only_prompt):
                if not active_streams.get(stream_id, False):
                    # Stream was stopped by client
                    print(f"⏹️ Stream被客户端停止: {stream_id}")
                    print(f"⏱️ 运行时间: {time.time() - request_start_time:.2f}秒")
                    return
                
                result_count += 1
                if result_count <= 3:  # Log first few results
                    print(f"📤 发送结果 #{result_count}: {str(result)[:200]}...")
                
                yield f"data: {json.dumps(result)}\n\n"
                
            print(f"✅ /write请求处理完成")
            print(f"📊 总计发送 {result_count} 个结果")
            print(f"⏱️ 总处理时间: {time.time() - request_start_time:.2f}秒")
            
        except Exception as e:
            error_start_time = time.time()
            print(f"\n{'='*60}")
            print(f"❌ /write请求处理失败")
            print(f"{'='*60}")
            print(f"🆔 Stream ID: {stream_id}")
            print(f"📝 Writer Mode: {writer_mode}")
            print(f"🤖 Main Model: {main_model}")
            print(f"🤖 Sub Model: {sub_model}")
            print(f"⏰ 错误发生时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            print(f"⏱️ 运行时间: {time.time() - request_start_time:.2f}秒")
            print(f"{'='*60}")
            print(f"❌ 错误类型: {type(e).__name__}")
            print(f"❌ 错误信息: {str(e)}")
            print(f"❌ 完整堆栈跟踪:")
            traceback.print_exc()
            print(f"{'='*60}")
            
            # 尝试获取更详细的错误信息
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'stream_id': stream_id,
                'writer_mode': writer_mode,
                'main_model': main_model,
                'sub_model': sub_model,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'runtime': f"{time.time() - request_start_time:.2f}秒"
            }
            
            # 如果有网络相关错误，记录更多信息
            if hasattr(e, 'response'):
                error_details['http_status'] = getattr(e.response, 'status_code', 'Unknown')
                error_details['http_headers'] = dict(getattr(e.response, 'headers', {}))
                try:
                    error_details['http_body'] = e.response.text[:1000] if hasattr(e.response, 'text') else str(e.response)[:1000]
                except:
                    error_details['http_body'] = 'Unable to read response body'
            
            print(f"📊 错误详情: {json.dumps(error_details, indent=2, ensure_ascii=False)}")
            
            error_msg = f"创作出错：\n错误类型: {type(e).__name__}\n错误信息: {str(e)}\n\n详细信息:\n- Stream ID: {stream_id}\n- 写作模式: {writer_mode}\n- 主模型: {main_model}\n- 副模型: {sub_model}\n- 运行时间: {time.time() - request_start_time:.2f}秒\n- 错误时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            
            # 添加特定错误类型的建议
            if 'timeout' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是超时错误，可能是模型响应过慢，建议:\n- 检查网络连接\n- 尝试使用更快的模型\n- 减少处理的文本量"
            elif 'api' in str(e).lower() and 'key' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是API密钥相关错误，建议:\n- 检查API密钥是否正确\n- 检查API密钥是否有效\n- 检查账户余额"
            elif 'connection' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是网络连接错误，建议:\n- 检查网络连接\n- 检查防火墙设置\n- 检查代理设置"
            
            error_chunk_list = [[*e[:2], error_msg] for e in chunk_list[chunk_span[0]:chunk_span[1]]]
            
            error_data = {
                "done": True,
                "chunk_type": "init",
                "chunk_list": error_chunk_list,
                "error": True,
                "error_details": error_details
            }
            
            yield f"data: {json.dumps(error_data)}\n\n"
            
        finally:
            # Clean up stream tracking
            if stream_id in active_streams:
                del active_streams[stream_id]
                print(f"🧹 清理Stream跟踪: {stream_id}")

    return Response(generate(), mimetype='text/event-stream')


@app.route('/summary', methods=['POST'])
def process_novel_text():
    data = request.json
    content = data['content']
    novel_name = data['novel_name']

    # Generate unique stream ID
    stream_id = str(time.time())
    active_streams[stream_id] = True
    
    # 记录请求信息
    print(f"\n{'='*60}")
    print(f"🌐 收到/summary请求")
    print(f"{'='*60}")
    print(f"📚 Novel Name: {novel_name}")
    print(f"🆔 Stream ID: {stream_id}")
    print(f"📄 Content Length: {len(content)} characters")
    print(f"🤖 Main Model: {data.get('main_model', 'Unknown')}")
    print(f"🤖 Sub Model: {data.get('sub_model', 'Unknown')}")
    print(f"⚙️ Settings: {data.get('settings', {})}")
    print(f"⏰ 请求时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print(f"{'='*60}\n")

    def generate():
        request_start_time = time.time()
        try:
            yield f"data: {json.dumps({'stream_id': stream_id})}\n\n"

            main_model = get_model_config_from_provider_model(data['main_model'])
            sub_model = get_model_config_from_provider_model(data['sub_model'])
            max_novel_summary_length = data['settings']['MAX_NOVEL_SUMMARY_LENGTH']
            max_thread_num = data['settings']['MAX_THREAD_NUM']
            
            print(f"📊 处理参数:")
            print(f"   📏 最大小说长度: {max_novel_summary_length}")
            print(f"   🔢 最大线程数: {max_thread_num}")
            print(f"   🤖 主模型配置: {main_model}")
            print(f"   🤖 副模型配置: {sub_model}")
            
            last_yield_time = 0
            result_count = 0
            
            for result in process_novel(content, novel_name, main_model, sub_model, max_novel_summary_length, max_thread_num):
                if not active_streams.get(stream_id, False):
                    # Stream was stopped by client
                    print(f"⏹️ Stream被客户端停止: {stream_id}")
                    print(f"⏱️ 运行时间: {time.time() - request_start_time:.2f}秒")
                    return
                
                result_count += 1
                if result_count <= 3:  # Log first few results
                    print(f"📤 发送结果 #{result_count}: {str(result)[:200]}...")
                
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
                
            print(f"✅ /summary请求处理完成")
            print(f"📊 总计发送 {result_count} 个结果")
            print(f"⏱️ 总处理时间: {time.time() - request_start_time:.2f}秒")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ /summary请求处理失败")
            print(f"{'='*60}")
            print(f"🆔 Stream ID: {stream_id}")
            print(f"📚 Novel Name: {novel_name}")
            print(f"📄 Content Length: {len(content)} characters")
            print(f"🤖 Main Model: {data.get('main_model', 'Unknown')}")
            print(f"🤖 Sub Model: {data.get('sub_model', 'Unknown')}")
            print(f"⏰ 错误发生时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            print(f"⏱️ 运行时间: {time.time() - request_start_time:.2f}秒")
            print(f"{'='*60}")
            print(f"❌ 错误类型: {type(e).__name__}")
            print(f"❌ 错误信息: {str(e)}")
            print(f"❌ 完整堆栈跟踪:")
            traceback.print_exc()
            print(f"{'='*60}")
            
            # 尝试获取更详细的错误信息
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'stream_id': stream_id,
                'novel_name': novel_name,
                'content_length': len(content),
                'main_model': data.get('main_model', 'Unknown'),
                'sub_model': data.get('sub_model', 'Unknown'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'runtime': f"{time.time() - request_start_time:.2f}秒"
            }
            
            # 如果有网络相关错误，记录更多信息
            if hasattr(e, 'response'):
                error_details['http_status'] = getattr(e.response, 'status_code', 'Unknown')
                error_details['http_headers'] = dict(getattr(e.response, 'headers', {}))
                try:
                    error_details['http_body'] = e.response.text[:1000] if hasattr(e.response, 'text') else str(e.response)[:1000]
                except:
                    error_details['http_body'] = 'Unable to read response body'
            
            print(f"📊 错误详情: {json.dumps(error_details, indent=2, ensure_ascii=False)}")
            
            error_msg = f"小说处理出错：\n错误类型: {type(e).__name__}\n错误信息: {str(e)}\n\n详细信息:\n- Stream ID: {stream_id}\n- 小说名称: {novel_name}\n- 内容长度: {len(content)} 字符\n- 主模型: {data.get('main_model', 'Unknown')}\n- 副模型: {data.get('sub_model', 'Unknown')}\n- 运行时间: {time.time() - request_start_time:.2f}秒\n- 错误时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            
            # 添加特定错误类型的建议
            if 'timeout' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是超时错误，可能是模型响应过慢，建议:\n- 检查网络连接\n- 尝试使用更快的模型\n- 减少处理的文本量"
            elif 'api' in str(e).lower() and 'key' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是API密钥相关错误，建议:\n- 检查API密钥是否正确\n- 检查API密钥是否有效\n- 检查账户余额"
            elif 'connection' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是网络连接错误，建议:\n- 检查网络连接\n- 检查防火墙设置\n- 检查代理设置"
            elif '长度' in str(e) or 'length' in str(e).lower():
                error_msg += f"\n\n💡 建议: 这是长度限制错误，建议:\n- 减少输入文本的长度\n- 增加系统的最大处理长度限制\n- 分段处理长文本"
            
            error_data = {
                "progress_msg": error_msg,
                "error": True,
                "error_details": error_details
            }
            
            yield f"data: {json.dumps(error_data)}\n\n"
            
        finally:
            # Clean up stream tracking
            if stream_id in active_streams:
                del active_streams[stream_id]
                print(f"🧹 清理Stream跟踪: {stream_id}")

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