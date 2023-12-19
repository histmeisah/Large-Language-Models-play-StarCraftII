import gym
import multiprocessing
from gym import spaces
import time
from sc2 import maps
from sc2.player import Bot
from sc2.main import run_game
import os
from config.config import map_race
from env.bot.Protoss_bot import Protoss_Bot
from env.bot.Zerg_bot import Zerg_Bot
from utils.action_info import ActionDescriptions
from typing import (
    Optional,
)


class Agent_vs_Agent_Env(gym.Env):
    def __init__(self, args):
        # 初始化
        self.replay_folder = args.replay_folder
        self.args = args
        self.process_id = args.process_id
        self.map_pool = args.map_pool
        self.map_idx = args.map_idx

        self.player1_race = args.player1_race
        self.player2_race = args.player2_race

        self.agent1_type = args.agent1_type  # LLM type or random type,for example,"gpt4","llama2","glm2","random"
        self.agent2_type = args.agent2_type  # LLM type or random type for example,"gpt4","llama2","glm2","random"

        self.map_name = self.map_pool[self.map_idx]

        # 为每个智能体创建独立的锁和transaction
        self.lock1 = multiprocessing.Manager().Lock()
        self.lock2 = multiprocessing.Manager().Lock()

        self.transaction1 = multiprocessing.Manager().dict()
        self.transaction2 = multiprocessing.Manager().dict()

        for transaction in [self.transaction1, self.transaction2]:
            transaction.update(
                {'information': [], 'reward': 0, 'action': None,
                 'done': False, 'result': None, 'iter': 0, 'command': None, "output_command_flag": False,
                 'action_executed': [], 'action_failures': [], })
        # 同步机制
        self.isReadyForNextStep1 = multiprocessing.Event()
        self.isReadyForNextStep2 = multiprocessing.Event()
        # 游戏结束标志
        self.game_end_event1 = multiprocessing.Event()
        self.game_end_event2 = multiprocessing.Event()
        # 游戏结束标志
        self.game_over1 = multiprocessing.Value('b', False)
        self.game_over2 = multiprocessing.Value('b', False)
        # 重置标志
        self.done_event1 = multiprocessing.Event()
        self.done_event2 = multiprocessing.Event()

        # 启动智能体进程
        self.p1 = None
        self.p2 = None

        # 设置动作空间
        self.action1_space = spaces.Discrete(self.calculate_action_space(self.player1_race))
        self.action2_space = spaces.Discrete(self.calculate_action_space(self.player2_race))

        # 设置观测空间
        self.observation1_space = spaces.Dict({
            "player_race": spaces.Text(max_length=20),  # Terran,Protoss, Zerg, Random
            "opposite_race": spaces.Text(max_length=20),  # Terran,Protoss, Zerg, Random
            "map_name": spaces.Text(max_length=20),  # Map name
            "information": spaces.Dict({
                "observation1": gym.spaces.Discrete(10),
                "observation2": gym.spaces.Box(low=0, high=1, shape=(3, 3)),
            }),  # Information about the game state
        })
        self.observation2_space = spaces.Dict({
            "player_race": spaces.Text(max_length=20),  # Terran,Protoss, Zerg, Random
            "opposite_race": spaces.Text(max_length=20),  # Terran,Protoss, Zerg, Random
            "map_name": spaces.Text(max_length=20),  # Map name
            "information": spaces.Dict({
                "observation1": gym.spaces.Discrete(10),
                "observation2": gym.spaces.Box(low=0, high=1, shape=(3, 3)),
            }),  # Information about the game state
        })

    def calculate_action_space(self, player_race):
        action_description = ActionDescriptions(player_race)
        action_list = action_description.action_descriptions
        return len(action_list)

    def check_process(self, agent_num, reset=False):
        # 根据传入的agent_num决定是操作哪个智能体的变量和进程
        p = self.p1 if agent_num == 1 else self.p2
        game_end_event = self.game_end_event1 if agent_num == 1 else self.game_end_event2
        lock = self.lock1 if agent_num == 1 else self.lock2
        transaction = self.transaction1 if agent_num == 1 else self.transaction2
        isReadyForNextStep = self.isReadyForNextStep1 if agent_num == 1 else self.isReadyForNextStep2
        done_event = self.done_event1 if agent_num == 1 else self.done_event2

        # 如果对应的进程存在且仍在运行
        if p is not None:
            if p.is_alive():
                # 如果游戏没有结束则直接返回，不重新启动进程
                if not game_end_event.is_set():
                    return
                # 如果游戏结束，则终止进程
                p.terminate()
            # 等待进程结束
            p.join()

        # 如果需要重置环境
        if reset:
            # 更新transaction字典，清空或重置一些字段
            self.transaction1.update(
                {'information': [], 'reward': 0, 'action': None,
                 'done': False, 'result': None, 'iter': 0, 'command': None, "output_command_flag": False,
                 'action_executed': [], 'action_failures': [], })
            self.transaction2.update(
                {'information': [], 'reward': 0, 'action': None,
                 'done': False, 'result': None, 'iter': 0, 'command': None, "output_command_flag": False,
                 'action_executed': [], 'action_failures': [], })

            # 清除游戏结束的事件标记
            self.game_end_event1.clear()
            self.game_end_event2.clear()

            # 启动新的agent_vs_agent进程
            p = multiprocessing.Process(target=agent_vs_agent, args=(
                self.transaction1, self.transaction2, self.lock1, self.lock2,
                self.isReadyForNextStep1, self.isReadyForNextStep2,
                self.game_end_event1, self.game_end_event2,
                self.done_event1, self.done_event2,
                self.map_name, self.replay_folder, self.process_id, self.args
            ))
            p.start()

            # 更新p1和p2
            self.p1 = p
            self.p2 = p

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        self.check_process(1, reset=True)
        self.check_process(2, reset=True)

        # 重置游戏结束标志
        self.game_end_event1.clear()
        self.game_end_event2.clear()

        state1 = {
            'player_race': self.player1_race,  # 玩家种族
            'opposite_race': self.player2_race,  # 对手种族
            'map_name': self.map_name,  # 地图名称
            'information': self.transaction1['information'],  # 游戏信息
            'action_executed': self.transaction1['action_executed'],  # 执行过的动作列表
            'action_failures': self.transaction1['action_failures']  # 失败的动作列表

        }

        state2 = {
            'player_race': self.player2_race,  # 玩家种族
            'opposite_race': self.player1_race,  # 对手种族
            'map_name': self.map_name,  # 地图名称
            'information': self.transaction2['information'],  # 游戏信息
            'action_executed': self.transaction2['action_executed'],  # 执行过的动作列表
            'action_failures': self.transaction2['action_failures']  # 失败的动作列表

        }

        return state1, state2

    def step(self, actions):
        # 这里假设actions是一个包含两个元素的列表，actions[0]是agent1的动作，actions[1]是agent2的动作
        actions_dict = {1: actions[0], 2: actions[1]}

        # 对每个智能体进行动作处理
        for agent_num, action in actions_dict.items():
            transaction = self.transaction1 if agent_num == 1 else self.transaction2
            lock = self.lock1 if agent_num == 1 else self.lock2

            with lock:
                if isinstance(action, tuple) and len(action) == 3:
                    action_, command, command_flag = action
                    transaction['action'] = action_
                    transaction['command'] = command
                    transaction['output_command_flag'] = command_flag
                else:
                    transaction['action'] = action
                    transaction['command'] = None
                    transaction['output_command_flag'] = False

        states, rewards, dones, infos = {}, {}, {}, {}

        for agent_num in [1, 2]:
            done_event = self.done_event1 if agent_num == 1 else self.done_event2
            isReadyForNextStep = self.isReadyForNextStep1 if agent_num == 1 else self.isReadyForNextStep2
            transaction = self.transaction1 if agent_num == 1 else self.transaction2
            player_race = self.player1_race if agent_num == 1 else self.player2_race
            opposite_race = self.player2_race if agent_num == 1 else self.player1_race
            game_over = self.game_over1 if agent_num == 1 else self.game_over2
            while not (done_event.is_set() or isReadyForNextStep.is_set()):
                time.sleep(0.0001)

            if done_event.is_set():
                done_event.clear()
                isReadyForNextStep.clear()
                game_over.value = True
                if transaction['result'].name == 'Victory':
                    transaction['reward'] += 50
            elif isReadyForNextStep.is_set():
                isReadyForNextStep.clear()
                self.check_process(agent_num)

            result = transaction['result']
            result_str = str(result) if result is not None else None

            states[agent_num] = {
                'player_race': player_race,
                'opposite_race': opposite_race,
                'map_name': self.map_name,
                'information': transaction['information'],
                'action_executed': transaction['action_executed'],
                'action_failures': transaction['action_failures']
            }

            for key, value in states[agent_num].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if not isinstance(sub_value, (int, float, str, bool, type(None))):
                            value[sub_key] = str(sub_value)
                    states[agent_num][key] = value

            rewards[agent_num] = transaction['reward']
            dones[agent_num] = transaction['done']
            infos[agent_num] = result_str
        # print("states:", states)
        # print(type(states))
        #
        # print("rewards:", rewards)
        # print(type(rewards))
        # print("dones:", dones)
        # print(type(dones))
        # print("infos:", infos)
        # print(type(infos))

        return states, rewards, dones, infos, None

    def render(self, mode='human'):
        return None

    def close(self):
        return None


def agent_vs_agent(transaction1, transaction2, lock1, lock2,
                   isReadyForNextStep1, isReadyForNextStep2,
                   game_end_event1, game_end_event2,
                   done_event1, done_event2,
                   map_name, replay_folder, process_id, args):
    map = map_name

    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(replay_folder):
        try:
            os.makedirs(replay_folder)
        except OSError:
            print(f"create dictionary {replay_folder} failure,please check and run program again.")
            return
    if args.player1_race == "Protoss":
        agent1 = Protoss_Bot
    elif args.player1_race == "Zerg":
        agent1 = Zerg_Bot
    else:
        raise ValueError("Now we only support Protoss and Zerg")
    if args.player2_race == "Protoss":
        agent2 = Protoss_Bot
    elif args.player2_race == "Zerg":
        agent2 = Zerg_Bot
    else:
        raise ValueError("Now we only support Protoss and Zerg")

    # result = run_multiple_games(
    #     [
    #         GameMatch(
    #             map_sc2=maps.get(map),
    #             players=[
    #                 Bot(
    #
    #                     map_race(args.player1_race), agent1(transaction1, lock1, isReadyForNextStep1)),
    #                 Bot(map_race(args.player2_race), agent2(transaction2, lock2, isReadyForNextStep2)),
    #             ],
    #             realtime=False
    #         )
    #     ]
    # )
    result = run_game(maps.get(map),
                      [Bot(

                          map_race(args.player1_race), agent1(transaction1, lock1, isReadyForNextStep1)),
                          Bot(map_race(args.player2_race), agent2(transaction2, lock2, isReadyForNextStep2))],
                      realtime=False,
                      save_replay_as=f'{replay_folder}/{args.current_time}_{map}_Agent1_{args.agent1_type}_vs_Agent2_{args.agent2_type}_process_{process_id}.SC2Replay')

    with lock1:
        transaction1['done'] = True
        transaction1['result'] = result[0]

    with lock2:
        transaction2['done'] = True
        transaction2['result'] = result[1]

    done_event1.set()  # Set done_event for agent1 when the game is over
    done_event2.set()  # Set done_event for agent2 when the game is over

    game_end_event1.set()  # Set game_end_event for agent1 when the game is over
    game_end_event2.set()  # Set game_end_event for agent2 when the game is over
