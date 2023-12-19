import json
def generate_summarize_L1(information):
    def create_summary(category_data):
        summary = ""
        for key, value in category_data.items():
            if isinstance(value, dict):  # 特殊处理带有子模块的情况
                sub_summary = create_summary(value)
                if sub_summary != "":
                    summary += f"\n{key.replace('_', ' ').capitalize()}:\n{sub_summary}"
            elif value != 0:  # 只在数值不为0时添加到总结
                summary += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
        return summary
    # 将字符串类型的值转换为字典
    for key in information:
        if isinstance(information[key], str):
            try:
                information[key] = json.loads(information[key].replace("'", "\""))  # 替换单引号为双引号，确保JSON格式正确
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse value of '{key}' as JSON. Value: {information[key]}")


    if not isinstance(information.get('resource'), dict):
        raise ValueError(f"Expected 'resource' to be a dictionary, but got: {type(information.get('resource'))}, value: {information.get('resource')}")

    game_time = information['resource'].get('game_time', "unknown time")

    summary = f"At {game_time} game time, our current StarCraft II situation is as follows:\n\n"

    categories = [
        ("Resources", information.get("resource", {})),
        ("Buildings", information.get("building", {})),
        ("Units", information.get("unit", {})),
        ("Planning", information.get("planning", {})),
        ("Research", information.get("research", {})),
        ("Enemy", information.get("enemy", {})),
        # ... 后续其他模块可以继续添加到这个列表中
    ]

    for category, category_data in categories:
        category_summary = create_summary(category_data)
        if category_summary != "":
            summary += f"{category}:\n{category_summary}\n"

    return summary
