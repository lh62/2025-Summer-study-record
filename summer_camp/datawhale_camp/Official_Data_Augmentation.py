import pandas as pd
import requests
import re
import json
from tqdm import tqdm

# 读取数据
data = pd.read_excel('summer_camp/datawhale_camp/data/info_table（训练+验证集）.xlsx')
data = data.fillna('无数据')

def call_llm(content: str):
    """
    调用大模型
    
    Args:
        content: 模型对话文本
    
    Returns:
        list: 问答对列表
    """
    # 调用大模型（硅基流动免费模型，推荐学习者自己申请）
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "user",
                "content": content  # 最终提示词，"/no_think"是关闭了qwen3的思考
            }
        ]
    }
    headers = {
        "Authorization": "Bearer sk-sxgcekfjoxwdfdtipzistkdslvoyhwocbfgxjklemuyqhkwx", # 替换自己的api token
        "Content-Type": "application/json"
    }
    resp = requests.request("POST", url, json=payload, headers=headers).json()
    # 使用正则提取大模型返回的json
    content = resp['choices'][0]['message']['content'].split('</think>')[-1]
    pattern = re.compile(r'^```json\s*([\s\S]*?)```$', re.IGNORECASE)  # 匹配 ```json 开头和 ``` 结尾之间的内容（忽略大小写）
    match = pattern.match(content.strip())  # 去除首尾空白后匹配
    if match:
        json_str = match.group(1).strip()  # 提取JSON字符串并去除首尾空白
        data = json.loads(json_str)
        return data
    else:
        return content

    return response['choices'][0]['message']['content']

def create_question_list(row: dict):
    """
    根据一行数创建问题列表
    
    Args:
        row: 一行数据的字典形式
    
    Returns:
        list: 问题列表
    """
    question_list = []
    # ----------- 添加问题列表数据 begin ----------- #
    # 检票口
    question_list.append(f'{row["车次"]}号车次应该从哪个检票口检票？')
    # 站台
    question_list.append(f'{row["车次"]}号车次应该从哪个站台上车？')
    # 目的地
    question_list.append(f'{row["车次"]}次列车的终到站是哪里？')
    
    # ----------- 添加问题列表数据 end ----------- #
    return question_list




# 简单问题的prompt
prompt = '''你是列车的乘务员，请你基于给定的列车班次信息回答用户的问题。
# 列车班次信息
{}

# 用户问题列表
{}

'''
output_format = '''# 输出格式
按json格式输出，且只需要输出一个json即可
```json
[{
    "q": "用户问题",
    "a": "问题答案"
},
...
]
```'''

train_data_list = []
error_data_list = []
# 提取列
cols = data.columns
# 遍历数据(baseline先10条数据)
i = 1
for idx, row in tqdm(data.iterrows(), desc='遍历生成答案', total=len(data)):
    try:
        # 组装数据
        row = dict(row)
        row['到点'] = str(row['到点'])
        row['开点'] = str(row['开点'])
        # 创建问题对
        question_list = create_question_list(row)
        # 大模型生成答案
        llm_result = call_llm(prompt.format(row, question_list) + output_format)
        # 总结结果
        train_data_list += llm_result
    except:
        error_data_list.append(row)
        continue


# 转换训练集
data_list = []
for data in tqdm(train_data_list, total=len(train_data_list)):
    if isinstance(data, str):
        continue
    data_list.append({'instruction': data['q'], 'output': data['a']})

json.dump(data_list, open('summer_camp/datawhale_camp/data/train.json', 'w', encoding='utf-8'), ensure_ascii=False)