import time
from core.parser_utils import parse_chapters
from core.summary_novel import summary_draft, summary_plot, summary_chapters
from config import MAX_NOVEL_SUMMARY_LENGTH, MAX_THREAD_NUM, ENABLE_ONLINE_DEMO

def batch_yield(generators, max_co_num=5, ret=[]):
    results = [None] * len(generators)
    yields = [None] * len(generators)
    finished = [False] * len(generators)

    while True:
        co_num = 0
        for i, gen in enumerate(generators):
            if finished[i]:
                continue

            try:
                co_num += 1
                yield_value = next(gen)
                yields[i] = yield_value
            except StopIteration as e:
                results[i] = e.value
                finished[i] = True
            
            if co_num >= max_co_num:
                    break
        
        if all(finished):
            break

        yield yields

    ret.clear()
    ret.extend(results)
    return ret

def process_novel(content, novel_name, model, sub_model, max_novel_summary_length, max_thread_num):
    import time
    
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"📚 小说处理开始")
    print(f"{'='*60}")
    print(f"📚 小说名称: {novel_name}")
    print(f"📄 内容长度: {len(content)} 字符")
    print(f"🤖 主模型: {model}")
    print(f"🤖 副模型: {sub_model}")
    print(f"📏 最大处理长度: {max_novel_summary_length}")
    print(f"🔢 最大线程数: {max_thread_num}")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"{'='*60}\n")
    
    # 统计信息
    total_cost = 0.0
    total_chars_generated = 0
    total_api_calls = 0
    currency_symbol = ''
    
    if ENABLE_ONLINE_DEMO:
        print(f"🌐 在线Demo模式检查...")
        if max_novel_summary_length > MAX_NOVEL_SUMMARY_LENGTH:
            error_msg = "在线Demo模型下，最大小说长度不能超过" + str(MAX_NOVEL_SUMMARY_LENGTH) + "个字符！"
            print(f"❌ 参数验证失败: {error_msg}")
            raise Exception(error_msg)
        if max_thread_num > MAX_THREAD_NUM:
            error_msg = "在线Demo模型下，最大线程数不能超过" + str(MAX_THREAD_NUM) + "！"
            print(f"❌ 参数验证失败: {error_msg}")
            raise Exception(error_msg)
        print(f"✅ 在线Demo模式参数验证通过")

    if len(content) > max_novel_summary_length:
        original_length = len(content)
        content = content[:max_novel_summary_length]
        print(f"⚠️ 内容截断: {original_length} → {len(content)} 字符")
        yield {"progress_msg": f"小说长度超出最大处理长度，已截断，只处理前{max_novel_summary_length}个字符。"}
        time.sleep(1)

    # Parse chapters
    parse_start_time = time.time()
    print(f"🔍 开始解析章节...")
    yield {"progress_msg": "正在解析章节..."}

    chapter_titles, chapter_contents = parse_chapters(content)
    parse_time = time.time() - parse_start_time
    
    chapter_count = len(chapter_titles)
    print(f"✅ 章节解析完成，耗时: {parse_time:.2f}秒")
    print(f"📊 解析结果: {chapter_count} 个章节")
    
    # 显示章节统计信息
    if chapter_count > 0:
        avg_chapter_length = sum(len(content) for content in chapter_contents) / chapter_count
        print(f"📊 章节统计:")
        print(f"   📄 平均章节长度: {avg_chapter_length:.0f} 字符")
        print(f"   📄 最长章节: {max(len(content) for content in chapter_contents)} 字符")
        print(f"   📄 最短章节: {min(len(content) for content in chapter_contents)} 字符")
        print(f"   📄 总内容长度: {sum(len(content) for content in chapter_contents)} 字符")

    yield {"progress_msg": "解析出章节数：" + str(chapter_count)}

    if chapter_count == 0:
        error_msg = "解析出章节数为0！！！"
        print(f"❌ 章节解析失败: {error_msg}")
        raise Exception(error_msg)

    # Process draft summaries
    draft_start_time = time.time()
    print(f"\n🔄 开始生成剧情摘要...")
    yield {"progress_msg": "正在生成剧情摘要..."}
    
    dw_list = []
    gens = [summary_draft(model, sub_model, ' '.join(title), content) for title, content in zip(chapter_titles, chapter_contents)]
    
    draft_processed = 0
    for yields in batch_yield(gens, ret=dw_list, max_co_num=max_thread_num):
        chars_num = sum([e['chars_num'] for e in yields if e is not None])
        current_cost = sum([e['current_cost'] for e in yields if e is not None])
        current_currency = next((e['currency_symbol'] for e in yields if e is not None), '')
        model_text = next((e['model'] for e in yields if e is not None), '')
        
        completed = sum([1 for e in yields if e is not None])
        if completed > draft_processed:
            draft_processed = completed
            total_cost += current_cost
            total_chars_generated += chars_num
            total_api_calls += completed
            currency_symbol = current_currency
            
            print(f"📊 剧情摘要进度: {completed}/{len(yields)} | 模型: {model_text} | 生成字符: {chars_num} | 花费: {current_cost:.4f}{current_currency}")
        
        yield {"progress_msg": f"正在生成剧情摘要 进度：{completed} / {len(yields)} 模型：{model_text} 已生成字符：{chars_num} 已花费：{current_cost:.4f}{current_currency}"}

    draft_time = time.time() - draft_start_time
    print(f"✅ 剧情摘要生成完成，耗时: {draft_time:.2f}秒")

    # Process plot summaries
    plot_start_time = time.time()
    print(f"\n🔄 开始生成章节大纲...")
    yield {"progress_msg": "正在生成章节大纲..."}
    
    cw_list = []
    gens = [summary_plot(model, sub_model, ' '.join(title), dw.x) for title, dw in zip(chapter_titles, dw_list)]
    
    plot_processed = 0
    for yields in batch_yield(gens, ret=cw_list, max_co_num=max_thread_num):
        chars_num = sum([e['chars_num'] for e in yields if e is not None])
        current_cost = sum([e['current_cost'] for e in yields if e is not None])
        current_currency = next((e['currency_symbol'] for e in yields if e is not None), '')
        model_text = next((e['model'] for e in yields if e is not None), '')
        
        completed = sum([1 for e in yields if e is not None])
        if completed > plot_processed:
            plot_processed = completed
            total_cost += current_cost
            total_chars_generated += chars_num
            total_api_calls += completed
            currency_symbol = current_currency
            
            print(f"📊 章节大纲进度: {completed}/{len(yields)} | 模型: {model_text} | 生成字符: {chars_num} | 花费: {current_cost:.4f}{current_currency}")
        
        yield {"progress_msg": f"正在生成章节大纲 进度：{completed} / {len(yields)} 模型：{model_text} 已生成字符：{chars_num} 已花费：{current_cost:.4f}{current_currency}"}

    plot_time = time.time() - plot_start_time
    print(f"✅ 章节大纲生成完成，耗时: {plot_time:.2f}秒")

    # Process chapter summaries
    outline_start_time = time.time()
    print(f"\n🔄 开始生成全书大纲...")
    yield {"progress_msg": "正在生成全书大纲..."}
    
    ow_list = []
    gens = [summary_chapters(model, sub_model, novel_name, chapter_titles, [cw.global_context['chapter'] for cw in cw_list])]
    
    for yields in batch_yield(gens, ret=ow_list, max_co_num=max_thread_num):
        chars_num = sum([e['chars_num'] for e in yields if e is not None])
        current_cost = sum([e['current_cost'] for e in yields if e is not None])
        current_currency = next((e['currency_symbol'] for e in yields if e is not None), '')
        model_text = next((e['model'] for e in yields if e is not None), '')
        
        total_cost += current_cost
        total_chars_generated += chars_num
        total_api_calls += 1
        currency_symbol = current_currency
        
        print(f"📊 全书大纲进度: 模型: {model_text} | 生成字符: {chars_num} | 花费: {current_cost:.4f}{current_currency}")
        
        yield {"progress_msg": f"正在生成全书大纲 模型：{model_text} 已生成字符：{chars_num} 已花费：{current_cost:.4f}{current_currency}"}

    outline_time = time.time() - outline_start_time
    print(f"✅ 全书大纲生成完成，耗时: {outline_time:.2f}秒")

    # Prepare final response
    print(f"\n🔄 准备最终响应...")
    response_start_time = time.time()
    
    outline = ow_list[0]
    plot_data = {}
    draft_data = {}

    for title, chapter_outline, cw, dw in zip(chapter_titles, [e[1] for e in outline.xy_pairs], cw_list, dw_list):
        chapter_name = ' '.join(title)
        plot_data[chapter_name] = {
            'chunks': [('', e) for e, _ in dw.xy_pairs],
            'context': chapter_outline # 不采用cw.global_context['chapter']，因为不含章节名
        }
        draft_data[chapter_name] = {
            'chunks': dw.xy_pairs,
            'context': ''  # Draft doesn't have global context
        }
    
    response_time = time.time() - response_start_time
    print(f"✅ 响应准备完成，耗时: {response_time:.2f}秒")

    # 最终统计信息
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"🎉 小说处理完成！")
    print(f"{'='*60}")
    print(f"📊 最终统计信息:")
    print(f"   📚 小说名称: {novel_name}")
    print(f"   📄 原始内容长度: {len(content)} 字符")
    print(f"   📖 章节数量: {chapter_count}")
    print(f"   🔄 总API调用数: {total_api_calls}")
    print(f"   💰 总花费: {total_cost:.4f}{currency_symbol}")
    print(f"   📄 总生成字符数: {total_chars_generated}")
    print(f"   ⏱️ 总处理时间: {total_time:.2f}秒")
    print(f"   📊 处理阶段耗时:")
    print(f"     🔍 章节解析: {parse_time:.2f}秒")
    print(f"     📝 剧情摘要: {draft_time:.2f}秒")
    print(f"     📋 章节大纲: {plot_time:.2f}秒")
    print(f"     📚 全书大纲: {outline_time:.2f}秒")
    print(f"     🔄 响应准备: {response_time:.2f}秒")
    print(f"   📈 性能指标:")
    print(f"     📈 平均每API调用用时: {total_time/total_api_calls:.2f}秒" if total_api_calls > 0 else "")
    print(f"     📈 平均每字符成本: {total_cost/total_chars_generated:.8f}{currency_symbol}" if total_chars_generated > 0 else "")
    print(f"     📈 生成效率: {total_chars_generated/total_time:.2f} 字符/秒" if total_time > 0 else "")
    print(f"     📈 处理效率: {len(content)/total_time:.2f} 原始字符/秒" if total_time > 0 else "")
    print(f"{'='*60}")

    final_response = {
        "progress_msg": "处理完成！",
        "outline": {
            "chunks": outline.xy_pairs,
            "context": outline.global_context['outline']
        },
        "plot": plot_data,
        "draft": draft_data,
        "stats": {
            "novel_name": novel_name,
            "original_length": len(content),
            "chapter_count": chapter_count,
            "total_api_calls": total_api_calls,
            "total_cost": total_cost,
            "currency_symbol": currency_symbol,
            "total_chars_generated": total_chars_generated,
            "total_time": total_time,
            "processing_stages": {
                "parse_time": parse_time,
                "draft_time": draft_time,
                "plot_time": plot_time,
                "outline_time": outline_time,
                "response_time": response_time
            }
        }
    }

    yield final_response
