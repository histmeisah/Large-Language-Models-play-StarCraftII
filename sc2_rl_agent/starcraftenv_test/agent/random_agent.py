import json
import os
from collections import deque
import random
from sc2_rl_agent.starcraftenv_test.summarize.L1_summarize import generate_summarize_L1


class RandomAgent:
    """
    随机agent: 用于测试环境

    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature, args,
                 action_description,
                 raw_observation="raw_observation.json", L1_observation_file_name="L1_observations.json",
                 commander_file_name='commander.json',
                 action_interval=10, request_delay=0.2, chunk_window=5, action_window=10, action_mix_rate=0.5,
                 last_k=5):
        self.args = args
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.system_prompt = system_prompt  # 系统提示
        self.temperature = temperature  # 生成文本的多样性
        self.raw_observation_file_name = raw_observation  # 保存原始观察的文件名
        self.L1_observation_file_name = L1_observation_file_name  # 保存L1观察的文件名
        self.commander_file_name = commander_file_name  # 保存命令的文件名
        self.raw_observations = []  # List to store raw_observations
        self.L1_observations = []  # List to store L1_observations
        self.commanders = []  # List to store commanders
        self.action_interval = action_interval  # 每隔几个step执行一个真实的动作
        self.current_step = 0  # 当前步数
        self.request_delay = request_delay  # 请求间隔
        self.example_prompt = example_prompt  # 例子输入
        self.action_queue = deque()
        self.summary_queue = deque()
        self.chunk_window = chunk_window
        self.action_window = action_window
        self.action_mix_rate = action_mix_rate
        self.last_k = last_k
        self.action_description = action_description
        self.action_dict = self.action_description.action_descriptions
        self.temp_command = "temp command"  # 用于保存临时的command
        self.current_time = args.current_time  # 获取当前时间
        self.game_info = self.generate_game_info()  # 生成游戏信息
        self.process_id = args.process_id
        self.current_step = 0  # 当前步数
        self.command_interval = 10  # 每10步进行一次command
        # 定义基础保存目录
        self.base_save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'log', 'random_log')

        # 为每一局游戏创建一个独立的文件夹，这里使用当前时间作为唯一标识符
        # 注意：您需要定义self.current_time 和 self.process_id
        self.game_folder = os.path.join(self.base_save_dir, f"game_{self.current_time}_{self.process_id}")

        # 如果目录不存在，创建它
        if not os.path.exists(self.game_folder):
            os.makedirs(self.game_folder)

    def _save_data_to_file(self, data, filename):
        """
        通用的数据保存方法
        :param data: 要保存的数据
        :param filename: 保存的文件名
        :return: None
        """
        full_path = os.path.join(self.game_folder, filename)
        with open(full_path, "a") as file:
            json.dump(data, file)
            file.write("\n")

    def _save_raw_observation_to_file(self, raw_observation):
        """
        保存观测信息
        :param raw_observation:
        :return: None
        """
        filename = "raw_observation.json"
        self._save_data_to_file(raw_observation, filename)

    def _save_action_executed_to_file(self, action_executed):
        """
        保存已执行的动作信息
        :param action_executed:
        :return: None
        """
        filename = "action_executed.json"
        self._save_data_to_file(action_executed, filename)

    def _save_action_failures_to_file(self, action_failures):
        """
        保存失败的动作信息
        :param action_failures:
        :return: None
        """
        filename = "action_failures.json"
        self._save_data_to_file(action_failures, filename)

    def _save_L1_observation_to_file(self, L1_observation):
        """
        保存L1 summarize后的信息
        :param L1_observation:L1 summarize后的信息
        :return: None
        """
        filename = "L1_observation.json"
        self._save_data_to_file(L1_observation, filename)

    def generate_game_info(self):
        """
        生成游戏信息
        地图
        玩家种族
        对手种族
        对手类型
        :return:
        """
        if self.args.num_agents == 'single':

            game_info = f"Map_{self.args.map_pool[self.args.map_idx]}_random_agent_Player_race_{self.args.player_race}_vs_{self.args.opposite_race}_opposite_type_{self.args.opposite_type}"
            return game_info
        elif self.args.num_agents == 'two':
            game_info = f"Map_{self.args.map_pool[self.args.map_idx]}_random_agent_Player1_race_{self.args.player1_race}_{self.args.agent1_type}_vs_{self.args.player2_race}_{self.args.agent1_type}"

    def action(self, observation):
        """
        随机agent的动作
        :param observation:
        :return:
        """

        # 直接从observation中提取相关信息
        player_race = observation['player_race']
        opposite_race = observation['opposite_race']
        map_name = observation['map_name']
        raw_observation = observation['information']
        action_executed = observation['action_executed']
        action_failures = observation['action_failures']

        # 保存原始观察数据
        self._save_raw_observation_to_file(raw_observation)

        # 保存已执行的动作和失败的动作数据
        self._save_action_executed_to_file(action_executed)
        self._save_action_failures_to_file(action_failures)
        if isinstance(raw_observation, dict):
            L1_observation = generate_summarize_L1(raw_observation)
            self._save_L1_observation_to_file(L1_observation)
        else:
            pass

        min_idx = 0
        flat_dict = {}
        for key, value in self.action_dict.items():
            for inner_key, inner_value in value.items():
                flat_dict[inner_key] = inner_value
        max_idx = len(flat_dict) - 1
        action = random.randint(min_idx, max_idx)

        # command 是和 action 对应的动作描述
        command = flat_dict[action]

        # 创建一个随机的命令标志
        command_flag = self.current_step % self.command_interval == 0
        # print(f"command_flag:{command_flag}")

        self.current_step += 1  # 更新步数
        return action, command, command_flag
