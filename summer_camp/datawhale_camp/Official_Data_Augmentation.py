import pandas as pd
import requests
import re
import json
from tqdm import tqdm
from datetime import datetime, timedelta

# 读取数据
data = pd.read_excel('summer_camp/datawhale_camp/data/info_table（训练+验证集）.xlsx')
data = data.fillna('无数据')
data_shang = data.copy()  # 保留原始数据用于后续处理
#data = data.iloc[100:]

print(f"数据加载完成，共{len(data)}条记录。")
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
        "model": "Qwen/Qwen3-30B-A3B-Instruct-2507",
        "messages": [#Qwen/Qwen3-30B-A3B-Instruct-2507
            {
                "role": "user",
                "content": content  # 最终提示词，"/no_think"是关闭了qwen3的思考
            }
        ]
    }
    headers = {
        "Authorization": "Bearer sk-oqbwacjmrrnbbynkovltxkrilyxxcfuafilrynqmltvshiif", # 替换自己的api token
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

def get_all_train_info(data: pd.DataFrame) -> str:
    """获取全部列车信息的格式化字符串"""
    train_info = []
    for _, row in data.iterrows():
        info = (f"车次: {row['车次']}, 始发站: {row['始发站']}, 终到站: {row['终到站']}, "
               f"到点: {row['到点']}, 开点: {row['开点']}, 候车厅: {row['候车厅']}, "
               f"检票口: {row['检票口']}, 站台: {row['站台']}")
        train_info.append(info)
    return "\n".join(train_info)

def create_question_list(row: dict, all_data: pd.DataFrame):
    """增强的问题生成策略，添加更复杂的分析类问题"""
    questions = []
    
    # 基础查询（保留原有的基础问题）
    questions.extend([
        f'{row["车次"]}号车次应该从哪个检票口检票？',
        f'{row["车次"]}号车次应该从哪个站台上车？',
        f'{row["车次"]}号车次的候车厅在哪里？',
        f'{row["车次"]}次列车的终到站是哪里？',
        f'{row["车次"]}号车次的始发站是哪里？',
        f'{row["车次"]}号车次的出发时间是什么时候？',
        f'{row["车次"]}号车次的到达时间是什么时候？',
    ])
    
    # 时间计算与推理
    questions.extend([
        f'{row["车次"]}号车次从{row["始发站"]}到{row["终到站"]}的实际运行时间是多少？',
        f'如果{row["车次"]}号车次延误1小时25分钟，最终到达时间是什么时候？',
        f'分析{row["车次"]}号车次在本站的停留时长，并与其他停留超过30分钟的车次进行对比。',
    ])
    
    # 多条件筛选
    questions.extend([
        f'筛选出满足以下全部条件的车次：1)和{row["车次"]}同一候车厅 2)发车时间在{row["开点"]}之后 3)使用相同站台',
        f'查找所有从{row["始发站"]}出发且行驶时间超过{row["车次"]}号车次的列车。',
        #f'统计{row["候车厅"]}内所有站台的车次分布情况。',
    ])
    
    # 异常场景处理
    questions.extend([
        f'如果{row["车次"]}号车次临时停运，寻找最近1小时内可替代的车次（考虑始发站和终到站）。',
        f'当{row["检票口"]}检票口临时关闭，{row["车次"]}号车次应该安排在哪个检票口？',
    ])
    
    # 跨行数据分析
    # questions.extend([
    #     #f'分析{row["候车厅"]}所有车次的发车时间分布，找出最拥挤的时间段。',
    #     #f'对比所有从{row["始发站"]}出发到{row["终到站"]}的车次：1)数量 2)平均行驶时间 3)最快/最慢路线',
    # ])
    
    # 添加复杂数据分析问题
    questions.extend([
        # 多维度分析
        #f'分析{row["候车厅"]}的车次分布特征：1)各时间段车次数量 2)各站台使用频率 3)高峰期建议',
        
        # 路线分析
        #f'分析从{row["始发站"]}到{row["终到站"]}的所有可能路线：1)直达车次 2)中转方案 3)最优建议',
        
        # 时间段分析
        #f'统计{row["开点"]}前后2小时内的车次密度，分析是否存在运力紧张问题',
        
        # 设施使用分析
        #f'分析{row["检票口"]}周边检票口的车次分布，评估是否需要分流',
        
        # 高峰期分析
        #f'找出所有和{row["车次"]}类似时间段的车次，分析：1)站台分布 2)候车厅容量压力 3)潜在拥堵风险',
        
        # 运力调配
        #f'如果{row["车次"]}停运，设计一个运力补充方案，考虑：1)备选车次 2)站台调整 3)客流分流',
        
        # 跨站分析
        #f'统计所有经过{row["始发站"]}和{row["终到站"]}的车次，分析：1)总数量 2)平均间隔 3)运力分布',
        
        # 线路优化
        #f'基于现有车次分布，分析是否需要在{row["开点"]}附近增开临时列车，并给出建议',
        
        # 应急预案
        #f'如遇{row["候车厅"]}局部拥堵，结合相邻候车厅的车次信息，制定分流预案',

        #f'若{row["车次"]}号车次开点为{row["开点"]}，到点为{row["到点"]}，请推理：1)是否跨天运行 2)实际运行时长 3)乘客最早/最晚到站时间'
    ])
    
    # # 添加逻辑推理类问题
    # questions.extend([
    #     # 时序逻辑推理
    #     f'若{row["车次"]}号车次开点为{row["开点"]}，到点为{row["到点"]}，请推理：1)是否跨天运行 2)实际运行时长 3)乘客最早/最晚到站时间',
        
    #     # 联动逻辑推理
    #     f'假设{row["候车厅"]}在早高峰期检票口出现故障，根据现有车次分布推理：1)最佳备用检票口 2)可能影响的车次数量 3)最优疏导方案',
        
    #     # 因果逻辑推理
    #     f'当{row["车次"]}号车次晚点超过2小时，连续推理可能造成的影响：1)后续车次延误概率 2)站台占用冲突 3)如何最小化影响范围',
        
    #     # 概率逻辑推理
    #     f'分析{row["始发站"]}至{row["终到站"]}区间的列车运行规律，推断：1)最可能延误的时段 2)最佳运力补充时间 3)客流高峰预测',
        
    #     # 条件逻辑推理
    #     f'如果同时满足：1){row["候车厅"]}客流饱和 2)邻近检票口拥堵 3){row["车次"]}晚点，推理最优解决方案',
        
    #     # 归纳逻辑推理
    #     f'根据所有经过{row["站台"]}的列车数据，归纳出：1)高峰期规律 2)最佳检票时间 3)站台使用效率提升建议',
        
    #     # 演绎逻辑推理
    #     f'基于{row["车次"]}的运行数据，推理出：1)是否为主要客流车次 2)运力安排是否合理 3)优化方向',
        
    #     # 系统逻辑推理
    #     f'分析整个车站的运营系统，当{row["车次"]}出现问题时：1)哪些环节会受影响 2)如何快速调整 3)需要协调的部门',
        
    #     # 连锁逻辑推理
    #     f'推理{row["车次"]}延误可能引发的连锁反应：1)影响范围 2)持续时间 3)如何快速恢复正常运营'
    # ])
    
    return questions




# 优化后的prompt模板
prompt = '''你是一位资深的列车调度员，请基于给定的列车时刻表信息回答问题。

# 数据说明
列车时刻表包含以下字段：
- 车次：列车的唯一编号
- 始发站/终到站：列车的起始和终点站
- 到点/开点：列车到达和发车的具体时间（24小时制）
- 候车厅/检票口/站台：与乘车相关的场地信息

# 列车时刻表数据
{}

# 当前查询车次
{}

# 回答要求

1. 回答问题时，请注意语言表达的准确性，避免出现语法错误；请注意回答的简洁性，避免过多陈述。

2. 对于时间计算类问题：
   - 考虑跨天的情况
   - 结果格式为"XX小时XX分钟"
   - 请注意回答的简洁性，避免过多陈述

3. 对于多条件筛选问题：
   - 逐一列举符合的车次
   - 说明筛选逻辑
   - 按时间顺序排列结果
   - 结果格式为"车次1,车次2,车次3"
   - 请注意回答的简洁性，避免过多陈述

4. 对于数据缺失情况：
   - 明确标注"无数据"
   - 说明可能的解决方案
   - 请注意回答的简洁性，避免过多陈述


# 用户问题
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
        row = dict(row)
        row['到点'] = str(row['到点'])
        row['开点'] = str(row['开点'])
        
        # 获取全局数据
        all_train_info = get_all_train_info(data_shang)
        question_list = create_question_list(row, data)
        
        # 在prompt中包含全局信息
        llm_result = call_llm(prompt.format(all_train_info, row, question_list) + output_format)
        print(1,llm_result)
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

json.dump(data_list, open('summer_camp/datawhale_camp/data/train6.json', 'w', encoding='utf-8'), ensure_ascii=False)