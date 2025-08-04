import json
from tqdm import tqdm

def convert_json_format(input_file, output_file):
    """
    读取train3.json格式的文件，将其转换为train2.json的格式，并保存到新文件。

    Args:
        input_file (str): 输入文件路径 (train3.json)
        output_file (str): 输出文件路径
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_file}' 未找到。")
        return
    except json.JSONDecodeError:
        print(f"错误: '{input_file}' 不是一个有效的JSON文件。")
        return

    # 确认原始数据是列表
    if not isinstance(original_data, list):
        print(f"错误: '{input_file}' 的顶层结构不是一个列表。")
        return

    converted_data = []
    print(f"开始转换文件 '{input_file}'...")
    
    # 使用tqdm显示进度条
    for item in tqdm(original_data, desc="转换进度"):
        # 原始格式: {"instruction": "question", "output": "answer"}
        # 目标格式: {"question": "answer"}
        if isinstance(item, dict) and 'instruction' in item and 'output' in item:
            question = item['instruction']
            answer = item['output']
            converted_data.append({question: answer})
        else:
            print(f"警告: 跳过一个格式不正确的条目: {item}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 使用indent=2参数使输出的JSON文件更具可读性
            json.dump(converted_data, f, ensure_ascii=False, indent=2)
        print(f"\n转换成功！数据已保存到 '{output_file}'。")
    except IOError as e:
        print(f"错误: 无法写入到文件 '{output_file}'. 错误信息: {e}")


if __name__ == '__main__':
    # 定义输入和输出文件名
    # 您可以根据需要修改这里的路径
    input_filename = 'summer_camp/datawhale_camp/data/train3.json'
    output_filename = 'summer_camp/datawhale_camp/data/train3_converted_to_train2_format.json'
    
    convert_json_format(input_filename, output_filename)