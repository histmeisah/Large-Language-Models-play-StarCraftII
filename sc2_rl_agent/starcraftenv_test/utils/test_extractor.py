import re


def extract_actions_from_text(text):
    # 正则表达式匹配模式：搜索 "Decisions" 之后的内容
    action_pattern = r"(?<=Decisions:)[\s\S]*"

    # 使用正则表达式从文本中找到所有匹配的决策部分
    decisions_matches = re.search(action_pattern, text)

    # 如果没有匹配结果，直接返回空列表
    if not decisions_matches:
        return []

    decisions_text = decisions_matches.group()

    # 使用另一个正则表达式从决策文本中提取实际的动作
    individual_actions_pattern = r"\d+: <?([^>\n]+)>?"
    actions = re.findall(individual_actions_pattern, decisions_text)

    return actions

import json

# 路径到您的JSON文件
file_path = 'F:\\python_code\\TextStarCraft2\\sc2_rl_agent\\starcraftenv_test\\log\\chatgpt_log\\game_20231005_153050_-1\\commander.json'

# 打开文件
data = []

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        if line.strip():  # 检查行是否为空
            data.append(json.loads(line))

for entry in data:
    print("______________________________________________________")
    result = extract_actions_from_text(entry[0])
    print(result)
    if not result:
        print(entry[0])
        raise ValueError("No actions found in the command text.")
#
# import re
#
#
# def test_regex_on_text(text):
#     action_pattern = r"\d+: <?([^>\n]+)>?"
#
#     # 使用正则表达式搜索 "Decisions" 开头的部分
#     decisions_match = re.search(r"\s*Decisions:\s*", text)
#
#     if not decisions_match:
#         print("Didn't find the start of the Decisions section.")
#         return []
#
#     # 从找到的匹配位置开始截取文本
#     decisions_text = text[decisions_match.start():]
#     print("Decisions Text:", decisions_text)
#
#     actions = re.findall(action_pattern, decisions_text)
#     print("Found Actions:", actions)
#
#
test_text = "# StarCraft II Game Analysis ... [your text truncated for brevity] ... Decisions:\n0: BUILD PROBE\n1: BUILD NEXUS"

print(extract_actions_from_text(test_text))