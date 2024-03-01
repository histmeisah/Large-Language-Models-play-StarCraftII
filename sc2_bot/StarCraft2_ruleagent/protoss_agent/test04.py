import ast


def extract_values_from_output(output_str):
    # 将字符串转化为字典
    output_dict = ast.literal_eval(output_str)

    # 提取字段
    building_supply = output_dict.get("building_supply")
    expansion = output_dict.get("expansion")
    produce_worker = output_dict.get("produce_worker")
    build_vespene = output_dict.get("build_vespene")
    CHRONOBOOSTENERGYCOST_upgrade = output_dict.get("CHRONOBOOSTENERGYCOST_upgrade")
    train_zealot = output_dict.get("train_zealot")
    train_stalker = output_dict.get("train_stalker")
    train_ht = output_dict.get("train_ht")
    train_archon = output_dict.get("train_archon")
    stalker_blink = output_dict.get("stalker_blink")
    research_blink = output_dict.get("research_blink")

    return {
        "building_supply": building_supply,
        "expansion": expansion,
        "produce_worker": produce_worker,
        "build_vespene": build_vespene,
        "CHRONOBOOSTENERGYCOST_upgrade": CHRONOBOOSTENERGYCOST_upgrade,
        "train_zealot": train_zealot,
        "train_stalker": train_stalker,
        "train_ht": train_ht,
        "train_archon": train_archon,
        "stalker_blink": stalker_blink,
        "research_blink": research_blink
    }


# 使用示例
output_str = "{\"building_supply\": None, \"expansion\": None, \"produce_worker\": None, \"build_vespene\": None, \"CHRONOBOOSTENERGYCOST_upgrade\": None, \"train_zealot\": None, \"train_stalker\": None, \"train_ht\": None, \"train_archon\": None, \"stalker_blink\": \"stalker_blink\", \"research_blink\": \"research_blink\"}"
values = extract_values_from_output(output_str)
print(values)
