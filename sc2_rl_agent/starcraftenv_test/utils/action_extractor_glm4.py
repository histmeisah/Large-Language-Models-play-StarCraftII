import re


def extract_actions_from_text(text):
    # 正则表达式匹配模式：搜索 "Decisions" 之后的每一行中括号内的内容
    action_pattern = r"Decisions:\n((?:.*\((.*)\)\n?)*)"

    # 使用正则表达式从文本中找到所有匹配的决策部分
    decisions_matches = re.search(action_pattern, text)

    # 如果没有匹配结果，直接返回空列表
    if not decisions_matches:
        return []

    decisions_text = decisions_matches.group(1)

    # 提取括号内的动作描述
    actions = re.findall(r"\(([^)]+)\)", decisions_text)

    return actions


def extract_actions_from_command(command, action_extractor, empty_idx, action_db_manager):
    extracted_decisions = extract_actions_from_text(command)

    # 如果没有提取到任何决策，返回一个空动作标记
    if not extracted_decisions:
        return [empty_idx], ["EMPTY ACTION"]

    action_ids, valid_actions = [], []
    for decision in extracted_decisions:
        ids, actions = action_extractor.extract_and_search_actions(decision, action_db_manager)
        action_ids.extend(ids)
        valid_actions.extend(actions)

    return action_ids, valid_actions


class ActionExtractor:
    def __init__(self, action_dict):
        self.full_action_dict = {}
        for category in action_dict:
            for key, value in action_dict[category].items():
                self.full_action_dict[value.upper()] = key

    def extract_and_search_actions(self, decision, action_db_manager):
        action = decision.upper()  # 转换为大写
        if action in self.full_action_dict:
            return [self.full_action_dict[action]], [action]
        else:
            # print(f"Searching for actions similar to: {action}")
            search_results = action_db_manager.search_actions(action)
            # print("Search results:", search_results)

            if search_results and 'ids' in search_results and 'documents' in search_results:
                actions = search_results['documents']
                if actions:  # 增加了这个检查
                    action_ids = search_results['ids']
                    print("vdb_return_action:", actions[0])
                    return [int(action_ids[0])], [actions[0]]  # 将最相近的动作的 ID 转换为整数并作为列表返回

            return [], []  # 如果没有找到匹配项，则返回空列表


if __name__ == "__main__":
    # 测试用的模型输出
    model_output = """
    Decisions:
    1. BUILD STRUCTURE: 19 (BUILD PYLON)
    2. BUILD STRUCTURE: 20 (BUILD ASSIMILATOR)
    3. TRAIN UNIT: 0 (TRAIN PROBE)
    4. RESEARCH TECHNIQUE: 34 (RESEARCH WARPGATERESEARCH) - after Pylon and more workers are available
    5. OTHER ACTION: 66 (CHRONOBOOST NEXUS) - to speed up Probe production
    """
    # 提取决策结果
    actions = extract_actions_from_text(model_output)

    # 打印结果
    print("Extracted Actions:")
    for action in actions:
        print(action)