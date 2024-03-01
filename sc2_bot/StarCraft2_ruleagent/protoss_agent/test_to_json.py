import json


def read_txt_file(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()
        # 转换为Python字典列表
        data = [eval(line) for line in content if line.strip()]
    return data


def transform_data(data, instruction_template):
    result = []

    for entry in data:
        output_data = {k: v for k, v in entry.items() if k != "information" and k != "iter"}

        # 转化为字符串，并替换null为None，并去除双引号的转义
        serialized_output = str(output_data).replace("\'", "\"").replace("\"None\"", "None")

        # 处理输入部分的字符串，去除\n
        input_str = entry.get("information", "").replace("\n", "")

        transformed_entry = {
            "instruction": instruction_template,
            "input": input_str,
            "output": serialized_output
        }
        result.append(transformed_entry)

    return result


def save_to_json(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    # 定义instruction_template内容
    instruction_template = "In this game of StarCraft II, we are representing the Protoss race against the Terran opponent. Our strategic approach involves primarily producing Stalkers and Zealots for offensive operations against the enemy."

    # 读取.txt文件
    data = read_txt_file(r"D:\python_code\TextStarCraft2\sc2_bot\StarCraft2_ruleagent\protoss_agent\transaction_logs.txt")

    # 转换数据格式
    transformed_data = transform_data(data, instruction_template)

    # 保存为.json文件
    save_to_json(transformed_data, "output2.json")


if __name__ == "__main__":
    main()
