import re
from caster_pig_prompt import early_game_response,early_game_response_2,early_game_response_3,early_game_response_4,early_game_response_5,early_game_response_6,early_game_response_7

# 定义一个函数来提取 "Game Situation Summary" 部分
def extract_game_situation_summary(text):
    # 定义正则表达式模式
    pattern = r"Game Situation Summary:(.*?)Comprehensive Analysis:"

    # 使用 re.search() 方法来搜索模式
    match = re.search(pattern, text, re.DOTALL)

    # 如果找到了匹配项，返回匹配到的文本
    if match:
        return match.group(1).strip()
    else:
        return None


# 定义一个包含多条游戏描述的列表
game_descriptions = [early_game_response,early_game_response_2,early_game_response_3,early_game_response_4,early_game_response_5,early_game_response_6,early_game_response_7]  # early_game_response 是你提供的文本变量

# 遍历列表，提取并打印 "Game Situation Summary" 部分
for description in game_descriptions:
    summary = extract_game_situation_summary(description)
    if summary:
        print("__________________________________________________________")
        print(summary)
        print("__________________________________________________________")
    else:
        print("未找到 'Game Situation Summary' 部分。")



