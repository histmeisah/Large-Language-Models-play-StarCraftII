import random
import json
from sc2_rl_agent.starcraftenv_test.summarize.L1_summarize import generate_summarize_L1
from sc2_bot.StarCraft2_ruleagent.protoss_agent.env_test.cal_llm import ChatBot_SingleTurn

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
        # print("observation is not a dict")
        return None

    # 获取 'information' 的值
    information = observation.get('information', None)

    if information is None:
        # print("information is None")
        return None

    # 如果 'information' 是一个字典，尝试获取 'game_time' 的值
    if isinstance(information, dict):
        game_time = information.get('game_time', None)
        if game_time is not None:
            return game_time
        else:
            # print("game_time is None")
            return None
    else:
        # print("information is not a dict")
        return None


def game_time_to_seconds(game_time_str):
    # 根据":"分割字符串
    minutes, seconds = map(int, game_time_str.split(":"))
    return minutes * 60 + seconds


class LLM_Agent:
    def __init__(self, system_prompt: str, port: int, host: str):
        self.action_space = ACTIONS
        self.last_action_time = None  # 上一次选择动作的时间
        self.system_prompt = system_prompt

        self.last_chosen_action = {key: None for key in self.action_space.keys()}  # 初始化为不采取任何动作
        self.chatbot = ChatBot_SingleTurn(model_name="fine_tuning", system_prompt=system_prompt, temperature=0.7,
                                          port=port, host=host)

    def extract_action_from_llm_output(self, llm_output):
        action = {}
        for key, possible_actions in self.action_space.items():
            if key in llm_output and llm_output[key] in possible_actions:
                action[key] = llm_output[key]
            else:
                action[key] = None
        return action

    def action(self, observation):
        raw_game_time = get_game_time(observation)
        if raw_game_time is not None:
            game_time = raw_game_time
        else:
            game_time = "00:00"

        # 将游戏时间转换为秒
        game_seconds = game_time_to_seconds(game_time)
        act_flag = False  # 初始设为 False，表示没有生成新动作

        # 如果游戏时间超过10秒，并且这是首次选择或距离上次选择已超过30秒
        if game_seconds >= 10 and (self.last_action_time is None or (game_seconds - self.last_action_time) >= 30):
            L1_summarization = generate_summarize_L1(observation['information'])
            llm_output_str = self.chatbot.query(L1_summarization)
            llm_output_str = llm_output_str.replace("None", "null")
            print("start_to_use_llm", llm_output_str)
            print("end")

            try:
                llm_output = json.loads(llm_output_str)
                self.last_chosen_action = self.extract_action_from_llm_output(llm_output)
                self.last_action_time = game_seconds  # 更新上次选择动作的时间
                act_flag = True  # 更新标志为 True，表示已生成新动作
            except json.JSONDecodeError:
                print("JSONDecodeError occurred.")
                # 使用您提供的备用动作
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

        return self.last_chosen_action, act_flag

    def choose_random_action(self):
        action = {}
        for key, possible_actions in self.action_space.items():
            action[key] = random.choice(possible_actions)
        return action


