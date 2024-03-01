import json
import os
import numpy as np
from sc2_rl_agent.starcraftenv_test.summarize.L1_summarize import generate_summarize_L1
from sc2_rl_agent.starcraftenv_test.summarize.gemini_test.L2_summarize import L2_summary
from collections import deque
from sc2_rl_agent.starcraftenv_test.utils.action_extractor import *
from sc2_rl_agent.starcraftenv_test.utils.action_vector_test import ActionDBManager


class GeminiAgent:
    """
    ChatGPTAgent
    接入大语言模型

    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature, args,
                 action_description,
                 raw_observation="raw_observation.json", L1_observation_file_name="L1_observations.json",
                 command_file_name='command.json',
                 action_interval=10, chunk_window=5, action_window=10, action_mix_rate=0.5,
                 last_k=5, prompt_type='v4'):
        self.args = args
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.system_prompt = system_prompt  # 系统提示
        self.temperature = temperature  # 生成文本的多样性
        self.raw_observation_file_name = raw_observation  # 保存原始观察的文件名
        self.L1_observation_file_name = L1_observation_file_name  # 保存L1观察的文件名
        self.command_file_name = command_file_name  # 保存命令的文件名
        self.raw_observations = []  # List to store raw_observations
        self.L1_observations = []  # List to store L1_observations
        self.commands = []  # List to store commands
        self.action_interval = action_interval  # 每隔几个step执行一个真实的动作
        self.current_step = 0  # 当前步数
        self.example_prompt = example_prompt  # 例子输入
        self.action_queue = deque()
        self.summary_queue = deque()
        self.executed_actions_queue = deque()
        self.failed_actions_queue = deque()
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
        self.empty_action_idx = self.get_empty_action_idx()
        self.base_save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'log', 'gemini_log')
        self.game_folder = os.path.join(self.base_save_dir, f"game_{self.current_time}_{self.process_id}")
        self.L2 = L2_summary(LLMapi_base=self.api_base, LLMapi_key=self.api_key, model_name=self.model_name,
                             temperature=self.temperature, system_prompt=self.system_prompt,
                             example_prompt=self.example_prompt, chunk_window=self.chunk_window,
                             prompt_type=prompt_type,game_folder=self.game_folder)
        self.get_opposite_bot_name()
        self.action_db_manager = self.init_action_db()
        # 为每一局游戏创建一个独立的文件夹，这里使用当前时间作为唯一标识符


        # 如果目录不存在，创建它
        if not os.path.exists(self.game_folder):
            os.makedirs(self.game_folder)

    def init_action_db(self):
        relative_path_parts = ["..", "..", "..", "utils", "actionvdb", "action_vdb"]
        action_vdb_path = os.path.join(*relative_path_parts)
        self.action_db = ActionDBManager(db_path=action_vdb_path)
        if self.args.player_race == "Protoss":
            self.action_db.initialize_collection("protoss_actions")
            return self.action_db
        elif self.args.player_race == "Zerg":
            self.action_db.initialize_collection("zerg_actions")
            return self.action_db
        else:
            raise ValueError("Not support Race")



    def preprocess_actions(self):
        # Convert executed actions to a list without 'EMPTY ACTION'
        executed_actions = [action for action in self.executed_actions_queue if action != "EMPTY ACTION"]

        # Convert failed actions to a structured format
        failed_actions_list = self.failed_actions_queue
        failed_actions_structured = []
        for failure in failed_actions_list:
            for f in failure:
                failed_actions_structured.append(f)

        return executed_actions, failed_actions_structured

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
        filename = "raw_observation.jsonl"
        # 如果观测数据为空，可以选择写入一个表示初始化或无数据状态的JSON对象
        if raw_observation == [] or raw_observation == {}:
            initial_data = {"info": "No observation data available at this frame."}
            self._save_data_to_file(initial_data, filename)
        else:
            self._save_data_to_file(raw_observation, filename)

    def _save_action_executed_to_file(self, action_executed):
        filename = "action_executed.jsonl"

        # 检查是否有执行的动作信息
        if action_executed:
            # 对于每个执行的动作，将其封装为一个JSON对象
            executed_info = {"action_executed": action_executed}
            self._save_data_to_file(executed_info, filename)
        else:
            # 如果没有执行的动作，可以选择记录一个表示无动作执行的状态
            # 下面是记录一个表示无动作执行的状态的示例
            no_action_info = {"action_executed": "No action executed in this step"}
            self._save_data_to_file(no_action_info, filename)

    def _save_action_failures_to_file(self, action_failures):
        filename = "action_failures.jsonl"

        # 检查是否有失败的动作信息
        if action_failures:
            for failure in action_failures:
                # 解析字符串中的动作和原因
                action, reason = failure.replace("Action failed: ", "").split(", Reason: ")
                # 将失败信息构造成一个JSON对象
                failure_info = {
                    "action": action,
                    "reason": reason
                }
                self._save_data_to_file(failure_info, filename)
        else:
            # 如果动作执行成功，可以选择记录成功状态或不记录
            # 下面是记录一个表示成功的状态的示例
            success_info = {"action_failure": "No action failures, action executed successfully"}
            self._save_data_to_file(success_info, filename)

    def _save_L1_observation_to_file(self, L1_observation):
        """
        保存L1 summarize后的信息，以文本形式封装在JSON对象中
        :param L1_observation: L1 summarize后的文本信息
        :return: None
        """
        filename = "L1_observation.jsonl"
        # 将文本信息封装为JSON对象
        data_to_save = {"observation": L1_observation}
        self._save_data_to_file(data_to_save, filename)

    def _save_command_to_file(self, command):
        """
        保存GPT输出的command信息，确保每个命令信息以JSON对象形式存储。
        :param command: GPT输出的command信息
        :return: None
        """
        filename = "command.jsonl"
        # 将命令信息封装为JSON对象
        if isinstance(command, list):
            # 如果命令是列表形式，对每个元素进行处理
            for cmd in command:
                command_info = {"command": cmd}
                self._save_data_to_file(command_info, filename)
        else:
            # 单个命令字符串直接封装并保存
            command_info = {"command": command}
            self._save_data_to_file(command_info, filename)

    def _save_combined_input_to_file(self, combined_input):
        """
        保存LLM决策时的输入
        :param combined_input:LLM决策时的输入
        :return: None
        """
        filename = "combined_input.jsonl"
        self._save_data_to_file(combined_input, filename)

    def get_empty_action_idx(self):
        flat_dict = {}
        for key, value in self.action_dict.items():
            for inner_key, inner_value in value.items():
                flat_dict[inner_key] = inner_value
        empty_action_idx = len(flat_dict) - 1
        return empty_action_idx

    def get_opposite_bot_name(self):
        if self.args.opposite_type == 'build_in':
            self.opposite_name = self.args.difficulty
        elif self.args.opposite_type == 'rule':
            self.opposite_name = self.args.opposite_bot
        else:
            raise ValueError("opposite_type must be build_in or rule")

    def generate_game_info(self):
        """
        生成游戏信息
        地图
        玩家种族
        对手种族
        对手类型
        :return:
        """
        if not hasattr(self, 'opposite_name'):
            self.get_opposite_bot_name()  # 如果尚未初始化，就调用方法来设置它
        # print("self.opposite_name", self.opposite_name)
        game_info = f"Map_{self.args.map_pool[self.args.map_idx]}_Player_race_{self.args.player_race}_vs_{self.args.opposite_race}_opposite_type_{self.args.opposite_type}_{self.opposite_name}"
        return game_info

    def _get_next_action(self):
        """

        :return:
        """
        # Check if there are actions in the queue
        if self.action_queue:
            # Return the first action and remove it from the queue
            return self.action_queue.popleft()
        else:
            empty_idx = self.empty_action_idx
            # If there are no actions, return empty action
            return empty_idx

    def extract_actions_from_command(self, command):
        if isinstance(command, list):
            command = " ".join(command)
        self.action_extractor = ActionExtractor(self.action_dict)
        empty_idx = self.action_description.empty_action_id
        action_ids, valid_actions = extract_actions_from_command(command, action_extractor=self.action_extractor,
                                                                 empty_idx=empty_idx,
                                                                 action_db_manager=self.action_db_manager)
        return action_ids, valid_actions


    def action(self, observation):
        """
        This function generates the next action for the ChatGPT agent to take.

        :param observation: The current observation from the environment.

        :return: The action that the ChatGPT agent should take, along with a command and a flag indicating whether a new command was generated.
        """

        # Extract the raw observation from the list and save it to a file.
        player_race = observation['player_race']
        opposite_race = observation['opposite_race']

        map_name = observation['map_name']
        raw_observation = observation['information']
        action_executed = observation['action_executed']
        action_failures = observation['action_failures']

        self.executed_actions_queue.append(action_executed)  # 存放executed_action
        self.failed_actions_queue.append(action_failures)  # 存放failed_action

        self._save_raw_observation_to_file(raw_observation)
        # 保存已执行的动作和失败的动作数据
        self._save_action_executed_to_file(action_executed)
        self._save_action_failures_to_file(action_failures)

        # If the raw observation is a dictionary, generate a level 1 summary and save it to a file. Otherwise, return the next action.
        if isinstance(raw_observation, dict):
            L1_observation = generate_summarize_L1(raw_observation)
            self._save_L1_observation_to_file(L1_observation)
        else:
            return self._get_next_action()

        # Add the new level 1 summary to the queue of summaries.
        self.summary_queue.append(L1_observation)  # 存放L1_summary

        # Initialize the command and the command flag. The command will contain the output of the level 2 summary model, and the flag will be True if a new command was generated.
        command = None  # 初始化command
        command_flag = False  # 初始化command_flag

        # If the current step is a multiple of the action interval and the summary queue is not empty, generate a level 2 summary and get a command.
        if self.current_step % self.action_interval == 0 and self.summary_queue:  # 每隔几个step执行一次
            # Convert the summary queue to a list and get the last k level 1 summaries.
            summaries = [list(self.summary_queue)]
            last_k_L1_summaries = self.L2.get_latest_k_messages(summaries, self.last_k)  # 获取最新的k个L1_summary
            executed, failed = self.preprocess_actions()  # 预处理已执行的动作和失败的动作

            combined_input = {
                'L1_summaries': last_k_L1_summaries,
                'executed_actions': executed,
                'failed_actions': failed
            }

            self._save_combined_input_to_file(combined_input)

            # Generate a level 2 summary and get a command.
            L2_summaries = self.L2.query(combined_input)
            command = L2_summaries

            # Save the command to a file and print it.
            self._save_command_to_file(command)
            self.temp_command = command
            print('command:', command)

            # Extract the action ids and values from the command.
            action_ids, action_values = self.extract_actions_from_command(
                command)  # 从command中提取action_ids和action_values

            # Mix the extracted actions with empty actions based on the mix rate.
            mixed_actions = self.mix_actions(action_ids)
            # print("mixed_actions:", mixed_actions)

            # Add the mixed actions to the action queue.
            self.action_queue.extend(mixed_actions)
            print("action_queue:", self.action_queue)

            # Clear the summary queue for the next cycle.
            # Clear the executed_queue and failed_queue for the next cycle.
            self.summary_queue.clear()
            self.executed_actions_queue.clear()
            self.failed_actions_queue.clear()

            # A new command was generated in this step, so set the command flag to True.
            command_flag = True

        # Increment the current step.
        self.current_step += 1

        # Get the next action from the action queue.
        action = self._get_next_action()

        # Log the raw observation, level 1 summary, command, and action to Weights & Biases.


        # Return the action, command, and command flag. The environment can use the command and command flag to display the command and whether it was newly generated.
        return action, command, command_flag

    def mix_actions(self, real_actions):
        """
        混合真实动作和空动作,用来实现每隔几个step执行一个真实的动作,其余的动作都是空动作,
        实现了动作的稀疏性,缓解了LLM的计算压力,使得LLM和游戏引擎可以较为正常的交互

        :param real_actions:
        :return:
        """
        empty_action = self.empty_action_idx
        mixed_actions = []
        # Calculate the number of real actions in each action_window
        num_real_actions = int(self.action_window * self.action_mix_rate)

        # Check the boundary conditions:
        # if the action_mix_rate is too high that requires more real_actions than we have, adjust it.
        if num_real_actions > len(real_actions):
            num_real_actions = len(real_actions)

        # The indices in the window where the real action should be placed
        real_action_indices = np.linspace(start=0, stop=self.action_window - 1, num=num_real_actions, dtype=int)

        for i in range(self.action_window):
            if i in real_action_indices and real_actions:
                mixed_actions.append(real_actions.pop(0))
            else:
                mixed_actions.append(empty_action)

        return mixed_actions