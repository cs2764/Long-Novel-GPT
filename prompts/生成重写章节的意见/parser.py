from promptflow.core import tool


@tool
def parse_response(response_msgs):
    from prompts.prompt_utils import parse_chunks_by_separators
    content = response_msgs[-1]['content']

    chunks = parse_chunks_by_separators(content, [r'\S*', ])
    if "改进意见" in chunks:
        return chunks["改进意见"]
    else:
        raise Exception(f"无法解析回复，找不到改进意见！")
