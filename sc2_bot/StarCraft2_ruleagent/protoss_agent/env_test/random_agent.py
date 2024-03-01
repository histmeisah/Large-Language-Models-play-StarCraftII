import random

ACTIONS = {
    "building_supply": [None, "building_supply"],
    "expansion": [None, "expansion"],
    "produce_worker": [None, "produce_worker"],
    "build_vespene": [None, "build_vespene"],
    "CHRONOBOOSTENERGYCOST_upgrade": [None, "CHRONOBOOSTENERGYCOST_upgrade"],
    "train_zealot": [None, "train_zealot"],
    "train_stalker": [None, "train_stalker"],
    "train_ht": [None, "train_ht"],
    "train_archon": [None, "train_archon"],
    "stalker_blink": [None, "stalker_blink"],
    "research_blink": [None, "research_blink"]
}


def get_game_time(observation):
    # 确保 observation 是一个字典
    if not isinstance(observation, dict):
        return None

    # 获取 'information' 的值
    information = observation.get('information', None)

    if information is None:
        return None

    # 如果 'information' 是一个字典，尝试获取 'game_time' 的值
    if isinstance(information, dict):
        game_time = information.get('game_time', None)
        if game_time is not None:
            return game_time
        else:

            return None
    else:
        return None


def game_time_to_seconds(game_time_str):
    # 根据":"分割字符串
    minutes, seconds = map(int, game_time_str.split(":"))
    return minutes * 60 + seconds


class RandomAgent:
    def __init__(self):
        self.action_space = ACTIONS
        self.last_action_time = None  # 上一次选择动作的时间
        self.last_chosen_action = {key: None for key in self.action_space.keys()}  # 初始化为不采取任何动作

    def action(self, observation):
        raw_game_time = get_game_time(observation)
        if raw_game_time is not None:
            game_time = raw_game_time
        else:
            game_time = "00:00"

        # 将游戏时间转换为秒
        game_seconds = game_time_to_seconds(game_time)

        act_flag = False  # 初始设为 False，表示没有生成新动作

        # 如果游戏时间超过4分钟，并且这是首次选择或距离上次选择已超过15秒
        if game_seconds >= 240 and (self.last_action_time is None or (game_seconds - self.last_action_time) >= 15):
            backup_action = {
                "building_supply": "building_supply",
                "expansion": "expansion",
                "produce_worker": "produce_worker",
                "build_vespene": "build_vespene",
                "CHRONOBOOSTENERGYCOST_upgrade": None,
                "train_zealot": "train_zealot",
                "train_stalker": "train_stalker",
                "train_ht": None,
                "train_archon": None,
                "stalker_blink": "stalker_blink",
                "research_blink": "research_blink"
            }
            self.last_chosen_action = backup_action
            self.last_action_time = game_seconds  # 更新上次选择动作的时间
            act_flag = True  # 更新标志为 True，表示已生成新动作
        #
        # print("type of game_time:", type(game_time))
        # print("game_time:", game_time)
        return self.last_chosen_action, act_flag  # 返回动作和标志

    def choose_random_action(self):
        action = {}
        for key, possible_actions in self.action_space.items():
            action[key] = random.choice(possible_actions)
        return action

